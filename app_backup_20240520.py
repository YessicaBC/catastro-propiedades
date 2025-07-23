import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
import time
import pandas as pd
from datetime import datetime
import os
import json
from pathlib import Path
import sqlite3
from sqlite3 import Error

def crear_mapa(coordenadas=None, zoom_start=13):
    """Crea un mapa centrado en las coordenadas dadas o en Independencia por defecto"""
    # Coordenadas por defecto: Comuna de Independencia
    default_coords = [-33.4172, -70.6506]
    
    if coordenadas:
        location = coordenadas
    else:
        location = default_coords
    
    m = folium.Map(location=location, zoom_start=zoom_start)
    return m

# Configuración de la página
st.set_page_config(
    page_title="Catastro Comunal de Independencia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la base de datos
DB_PATH = 'catastro_propiedades.db'
UPLOAD_FOLDER = 'uploads'

# Crear directorios necesarios
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def get_db_connection():
    """Crea una conexión a la base de datos SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Habilitar claves foráneas
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Tabla de propiedades
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS propiedades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT NOT NULL,
                propietario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                rol_propiedad TEXT NOT NULL,
                avaluo_total REAL NOT NULL,
                destino_sii TEXT,
                destino_dom TEXT,
                patente_comercial TEXT,
                num_contacto TEXT,
                coordenadas TEXT,
                fiscalizacion_dom TEXT,
                m2_terreno REAL,
                m2_construidos REAL,
                linea_construccion TEXT,
                ano_construccion INTEGER,
                expediente_dom TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(rut, rol_propiedad)
            )
            ''')
            
            # Tabla de fotos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                propiedad_id INTEGER,
                ruta_archivo TEXT NOT NULL,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (propiedad_id) REFERENCES propiedades (id) ON DELETE CASCADE
            )
            ''')
            
            # Crear índices para búsquedas frecuentes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_propiedades_rut ON propiedades(rut)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_propiedades_rol ON propiedades(rol_propiedad)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fotos_propiedad ON fotos(propiedad_id)')
            
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error al inicializar la base de datos: {e}")
            return False
        finally:
            conn.close()
    return False

def guardar_propiedad(propiedad):
    """Guarda una nueva propiedad en la base de datos"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Insertar propiedad
            cursor.execute('''
            INSERT OR REPLACE INTO propiedades (
                rut, propietario, direccion, rol_propiedad, avaluo_total,
                destino_sii, destino_dom, patente_comercial, num_contacto,
                coordenadas, fiscalizacion_dom, m2_terreno, m2_construidos,
                linea_construccion, ano_construccion, expediente_dom, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                propiedad['RUT'], propiedad['Propietario'], propiedad['Dirección'],
                propiedad['ROL Propiedad'], propiedad['Avalúo Total'], propiedad['Destino SII'],
                propiedad['Destino DOM'], propiedad['Patente Comercial'], propiedad['N° de contacto'],
                propiedad['Coordenadas'], propiedad['Fiscalización DOM'], propiedad['M2 Terreno'],
                propiedad['M2 Construidos'], propiedad['Línea de Construcción'],
                propiedad['Año de Construcción'], propiedad['Expediente DOM'], propiedad['Observaciones']
            ))
            
            propiedad_id = cursor.lastrowid
            conn.commit()
            return propiedad_id
        except Error as e:
            st.error(f"Error al guardar la propiedad: {e}")
            return None
        finally:
            conn.close()
    return None

def guardar_fotos(propiedad_id, fotos):
    """Guarda las rutas de las fotos en la base de datos"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Primero eliminamos las fotos existentes
            cursor.execute('DELETE FROM fotos WHERE propiedad_id = ?', (propiedad_id,))
            # Luego insertamos las nuevas
            for foto in fotos:
                cursor.execute(
                    'INSERT INTO fotos (propiedad_id, ruta_archivo) VALUES (?, ?)',
                    (propiedad_id, foto)
                )
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error al guardar las fotos: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def obtener_propiedades(pagina=1, por_pagina=10, filtros=None):
    """Obtiene propiedades paginadas con filtros opcionales"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Construir consulta con filtros
            query = 'SELECT * FROM propiedades'
            params = []
            
            if filtros:
                condiciones = []
                for campo, valor in filtros.items():
                    if valor:
                        condiciones.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")
                
                if condiciones:
                    query += ' WHERE ' + ' AND '.join(condiciones)
            
            # Contar total de registros
            count_query = 'SELECT COUNT(*) FROM (' + query + ')'
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Aplicar paginación
            offset = (pagina - 1) * por_pagina
            query += ' ORDER BY fecha_creacion DESC LIMIT ? OFFSET ?'
            params.extend([por_pagina, offset])
            
            cursor.execute(query, params)
            columnas = [desc[0] for desc in cursor.description]
            propiedades = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
            
            # Obtener fotos para cada propiedad
            for propiedad in propiedades:
                cursor.execute(
                    'SELECT ruta_archivo FROM fotos WHERE propiedad_id = ?',
                    (propiedad['id'],)
                )
                propiedad['Fotos'] = [foto[0] for foto in cursor.fetchall()]
            
            return {
                'datos': propiedades,
                'total': total,
                'pagina': pagina,
                'por_pagina': por_pagina,
                'total_paginas': (total + por_pagina - 1) // por_pagina
            }
            
        except Error as e:
            st.error(f"Error al obtener propiedades: {e}")
            return {'datos': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'total_paginas': 0}
        finally:
            conn.close()
    return {'datos': [], 'total': 0, 'pagina': 1, 'por_pagina': por_pagina, 'total_paginas': 0}

# Inicializar la base de datos al inicio
if 'db_initialized' not in st.session_state:
    if init_db():
        st.session_state.db_initialized = True
    else:
        st.error("No se pudo inicializar la base de datos. La aplicación podría no funcionar correctamente.")

# Configuración de la barra lateral
with st.sidebar:
    st.image("https://www.municipalidaddesantiago.cl/wp-content/uploads/2021/12/logo-municipalidad-santiago.png", width=200)
    st.title("Catastro Comunal")
    st.markdown("---")
    opcion = st.radio(
        "Menú Principal",
        ["Inicio", "Agregar Propiedad", "Ver/Editar Propiedades", "Reportes"],
        index=0
    )
    st.markdown("---")
    st.markdown("### Acerca de")
    st.markdown("Sistema de Catastro de la Comuna de Independencia")
    st.markdown("Versión 1.0.0")

# Página de inicio
if opcion == "Inicio":
    st.title("Bienvenido al Sistema de Catastro")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Estadísticas Rápidas")
        
        # Obtener estadísticas de la base de datos
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Total de propiedades
                cursor.execute("SELECT COUNT(*) FROM propiedades")
                total_propiedades = cursor.fetchone()[0]
                
                # Propiedades por tipo de destino SII
                cursor.execute("""
                    SELECT destino_sii, COUNT(*) as cantidad 
                    FROM propiedades 
                    WHERE destino_sii IS NOT NULL AND destino_sii != ''
                    GROUP BY destino_sii
                    ORDER BY cantidad DESC
                """)
                destinos = cursor.fetchall()
                
                # Últimas propiedades agregadas
                cursor.execute("""
                    SELECT propietario, direccion, fecha_creacion 
                    FROM propiedades 
                    ORDER BY fecha_creacion DESC 
                    LIMIT 5
                """)
                ultimas_propiedades = cursor.fetchall()
                
            except Error as e:
                st.error(f"Error al obtener estadísticas: {e}")
            finally:
                conn.close()
        
        # Mostrar tarjetas con estadísticas
        st.metric("Total de Propiedades", total_propiedades)
        
        if destinos:
            st.markdown("#### Propiedades por Destino SII")
            for destino, cantidad in destinos:
                st.markdown(f"- **{destino}**: {cantidad} propiedades")
    
    with col2:
        st.markdown("### 📍 Mapa de la Comuna")
        # Mapa centrado en Independencia
        m = crear_mapa()
        folium_static(m, width=400, height=400)
    
    st.markdown("---")
    st.markdown("### Últimas Propiedades Agregadas")
    
    if 'ultimas_propiedades' in locals() and ultimas_propiedades:
        for prop in ultimas_propiedades:
            with st.expander(f"{prop[0]} - {prop[1]}"):
                st.write(f"**Fecha de registro:** {prop[2]}")
                st.button("Ver detalles", key=f"ver_{prop[0]}")
    else:
        st.info("No hay propiedades registradas aún.")

# Configuración de estilos personalizados
st.markdown("""
<style>
    .main {padding: 0rem 1rem 1rem 1rem;}
    .stButton>button {width: 100%; background-color: #4CAF50; color: white;}
    .stTextInput>div>div>input {background-color: #f8f9fa;}
    .stSelectbox>div>div>select {background-color: #f8f9fa;}
    .stNumberInput>div>div>input {background-color: #f8f9fa;}
    div.stButton > button:hover {background-color: #45a049;}
    div[data-testid="stForm"] {background-color: #ffffff; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);}
    div.block-container {padding-top: 1rem;}
    div[data-testid="stSidebar"] > div:first-child {background-color: #f8f9fa;}
    h1 {color: #1e3d59; margin-bottom: 2rem;}
    h2 {color: #1e3d59; margin-bottom: 1rem;}
    .success-message {padding: 1rem; border-radius: 5px; background-color: #d4edda; color: #155724; margin: 1rem 0;}
    .error-message {padding: 1rem; border-radius: 5px; background-color: #f8d7da; color: #721c24; margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)

# Contenedor principal con padding
with st.container():
    # Título principal con ícono
    st.markdown("""<h1>📋 Catastro Comunal de Independencia</h1>""", unsafe_allow_html=True)
    
    # Línea separadora
    st.markdown("---")

# Menú lateral con estilo
with st.sidebar:
    st.markdown("""<h2>🔍 Menú de Navegación</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='margin-bottom: 2rem;'>Seleccione una opción para comenzar</p>""", unsafe_allow_html=True)
    
    opcion = st.selectbox(
        "",
        ["Agregar Propiedad", "Ver/Editar Propiedades", "Buscar Propiedades", "Gestionar Fotos", "Exportar Datos"],
        format_func=lambda x: {
            "Agregar Propiedad": "📝 Agregar Propiedad",
            "Ver/Editar Propiedades": "📋 Ver/Editar Propiedades",
            "Buscar Propiedades": "🔍 Buscar Propiedades",
            "Gestionar Fotos": "🖼️ Gestionar Fotos",
            "Exportar Datos": "📊 Exportar Datos"
        }[x]
    )
    

    st.markdown("---")
    st.markdown("""<p style='font-size: 0.8rem; color: #666;'>Sistema de Catastro Municipal</p>""", unsafe_allow_html=True)

def parse_coordenadas(coord_str):
    """Convierte string de coordenadas a tupla de flotantes (lat, lon)"""
    try:
        if ',' not in coord_str:
            return None
        lat, lon = coord_str.split(',')
        lat = float(lat.strip())
        lon = float(lon.strip())
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
        return None
    except:
        return None


def validar_rut(rut):
    """
    Valida un RUT chileno en formato:
    - 12345678-9
    - 12.345.678-9
    - 123456789 (sin formato)
    """
    # Limpiar el RUT: quitar puntos, guión y espacios, convertir a mayúsculas
    rut = rut.strip().upper().replace('.', '').replace('-', '').replace(' ', '')
    
    # Validar longitud mínima (sin dígito verificador: 1, con dígito verificador: 2)
    if len(rut) < 2:
        return False
    
    # Separar el cuerpo del dígito verificador
    cuerpo = rut[:-1]
    verificador = rut[-1]
    
    # Validar que el cuerpo sean solo dígitos
    if not cuerpo.isdigit():
        return False
    
    # Validar que el dígito verificador sea un dígito o K
    if not (verificador.isdigit() or verificador == 'K'):
        return False
    
    # Calcular el dígito verificador esperado
    suma = 0
    multiplicador = 2
    
    # Recorrer el cuerpo del RUT de derecha a izquierda
    for c in reversed(cuerpo):
        suma += int(c) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    
    # Calcular el dígito verificador
    resto = suma % 11
    dvr = 11 - resto
    
    # Casos especiales
    if dvr == 11:
        dvr = '0'
    elif dvr == 10:
        dvr = 'K'
    else:
        dvr = str(dvr)
    
    # Comparar con el dígito verificador ingresado
    return verificador == dvr

if opcion == "Agregar Propiedad":
    st.markdown("""
        <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; margin-bottom:30px;'>
            <h2 style='color:#1e3d59; margin:0;'>📝 Agregar Nueva Propiedad</h2>
            <p style='color:#666; margin:5px 0 0 0;'>Complete el formulario con los datos de la propiedad</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("formulario_propiedad"):
        # Sección 1: Información Básica
        with st.expander("📋 Información Básica", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                rut = st.text_input("RUT Propietario *", help="Formato: 12345678-9")
            with col2:
                propietario = st.text_input("Propietario *")
            
            num_contacto = st.text_input("N° de contacto *", help="Número de teléfono de contacto")
            direccion = st.text_area("Dirección *", height=70)
        
        # Sección 2: Detalles de la Propiedad
        with st.expander("🏠 Detalles de la Propiedad", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                rol = st.text_input("ROL Propiedad *")
                avaluo = st.number_input("Avalúo Total *", min_value=0, step=1000, format="%d")
                m2_terreno = st.number_input("M² Terreno *", min_value=0.0, step=0.01)
                m2_construidos = st.number_input("M² Construidos *", min_value=0.0, step=0.01)
                
            with col2:
                año_construccion = st.number_input(
                    "Año de Construcción", 
                    min_value=1800, 
                    max_value=datetime.now().year,
                    value=datetime.now().year
                )
                expediente = st.text_input("Expediente DOM")
        
        # Sección 3: Clasificación y Fiscalización
        with st.expander("📋 Clasificación y Fiscalización", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                destino_sii = st.text_input("Destino SII")
                destino_dom = st.text_input("Destino DOM")
                
            with col2:
                fiscalizada = st.selectbox(
                    "Fiscalización DOM *",
                    options=["", "CONSTRUCCION REGULARIZADA", "CONSTRUCCION IRREGULAR"],
                    index=0,
                    help="Seleccione el estado de fiscalización"
                )
                
                patente_comercial = st.selectbox(
                    "PATENTE COMERCIAL *",
                    options=["", "PATENTE AL DIA", "PATENTE MOROSA", "SIN PATENTE"],
                    index=0,
                    help="Seleccione el estado de la patente"
                )
        
        # Sección 4: Línea de Construcción Detallada
        with st.expander("🏗️ Detalles de la Construcción", expanded=False):
            st.markdown("**Línea de Construcción**")
            
            # Lista para almacenar los valores de cada línea
            lineas_construccion = []
            
            # Crear 6 filas de campos
            for i in range(1, 7):
                st.markdown(f"**Línea {i}**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    materialidad = st.selectbox(
                        f"Materialidad {i}",
                        options=["", "Hormigón", "Acero", "Madera", "Mixto", "Otro"],
                        index=0,
                        key=f"materialidad_{i}",
                        help=f"Seleccione el material principal de construcción para la línea {i}"
                    )
                
                with col2:
                    año = st.selectbox(
                        f"Año {i}",
                        options=[""] + list(range(datetime.now().year, 1800, -1)),
                        index=0,
                        key=f"año_{i}",
                        help=f"Año de construcción para la línea {i}"
                    )
                
                with col3:
                    # Usar number_input con el mismo formato que M² Construidos
                    m2 = st.number_input(
                        f"M² {i}",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        value=None,
                        key=f"m2_{i}",
                        help=f"Metros cuadrados construidos para la línea {i}"
                    )
                
                # Agregar a la lista si al menos un campo tiene valor
                if materialidad or año or m2 is not None:
                    # Formatear M² con dos decimales si tiene valor
                    m2_display = f"{m2:.2f} m²" if m2 is not None else ""
                    linea = f"{materialidad} {año} {m2_display}".strip()
                    lineas_construccion.append(linea)
                
                # Agregar un pequeño espacio entre líneas
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            
            # Combinar todas las líneas en un solo string
            linea_construccion = " | ".join(filter(None, lineas_construccion))
        
        # Sección 5: Ubicación
        with st.expander("📍 Ubicación en Mapa", expanded=False):
            coordenadas = st.text_input(
                "Coordenadas (Lat, Long)", 
                placeholder="Ej: -33.4172, -70.6506",
                help="Ingrese las coordenadas en formato: latitud, longitud"
            )
            
            if coordenadas:
                coords = parse_coordenadas(coordenadas)
                if coords:
                    st.success("✅ Coordenadas válidas")
                    m = crear_mapa(coords)
                    folium.Marker(
                        coords,
                        popup=f"{propiedad if 'propiedad' in locals() else 'Nueva propiedad'}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
                    folium_static(m, width=700)
                else:
                    st.error("❌ Formato de coordenadas inválido. Use: latitud, longitud")
        
        # Sección 6: Observaciones
        with st.expander("📝 Observaciones Adicionales", expanded=False):
            observaciones = st.text_area("Ingrese cualquier observación adicional", height=100)
        
        # Botón de envío
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "💾 Guardar Propiedad", 
                use_container_width=True,
                type="primary"
            )
        
        st.markdown("<div style='margin: 10px 0;'><small>* Campos obligatorios</small></div>", unsafe_allow_html=True)
        
        if submitted:
            if not validar_rut(rut):
                st.markdown("""<div class='error-message'>❌ RUT inválido. Por favor verifique el formato y el dígito verificador.</div>""", unsafe_allow_html=True)
            else:
                # Mostrar spinner durante el proceso
                with st.spinner('Guardando información...'):
                    time.sleep(0.5)  # Simular proceso
                    nueva_propiedad = {
                        'RUT': rut,
                        'Propietario': propietario,
                        'Dirección': direccion,
                        'ROL Propiedad': rol,
                        'Avalúo Total': avaluo,
                        'Destino SII': destino_sii,
                        'Destino DOM': destino_dom,
                        'Patente Comercial': patente_comercial,
                        'N° de contacto': num_contacto,
                        'Coordenadas': coordenadas,
                        'Fiscalización DOM': fiscalizada,
                        'M2 Terreno': m2_terreno,
                        'M2 Construidos': m2_construidos,
                        'Línea de Construcción': linea_construccion,
                        'Año de Construcción': año_construccion,
                        'Expediente DOM': expediente,
                        'Observaciones': observaciones,
                        'Fotos': []  # Inicializar lista vacía para fotos
                    }
                    propiedad_id = guardar_propiedad(nueva_propiedad)
                    if propiedad_id:
                        st.markdown("""<div class='success-message'>✅ Propiedad agregada exitosamente!</div>""", unsafe_allow_html=True)
                    else:
                        st.error("Error al guardar los datos. Por favor, intente nuevamente.")

elif opcion == "Ver/Editar Propiedades":
    st.markdown("""<h2>📋 Lista de Propiedades</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Visualice y edite las propiedades registradas</p>""", unsafe_allow_html=True)
    
    # Crear pestañas para tabla, mapa y estadísticas
    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Datos", "🗺️ Mapa de Propiedades", "📈 Estadísticas"])
    
    propiedades = obtener_propiedades()
    
    if len(propiedades['datos']) > 0:
        with tab1:
            edited_df = pd.DataFrame(propiedades['datos'])
            if not edited_df.empty:
                edited_df = st.data_editor(edited_df, num_rows="dynamic")
                if not edited_df.equals(pd.DataFrame(propiedades['datos'])):
                    # Actualizar propiedades en la base de datos
                    for i, propiedad in edited_df.iterrows():
                        guardar_propiedad(propiedad.to_dict())
                    st.success("¡Cambios guardados exitosamente!")
            else:
                st.info("No hay propiedades registradas.")
        
        with tab2:
            m = crear_mapa()
            # Agregar marcadores para cada propiedad con coordenadas válidas
            for propiedad in propiedades['datos']:
                if isinstance(propiedad['Coordenadas'], str):
                    coords = parse_coordenadas(propiedad['Coordenadas'])
                    if coords:
                        folium.Marker(
                            coords,
                            popup=f"ROL Propiedad: {propiedad['ROL Propiedad']}<br>Dirección: {propiedad['Dirección']}<br>Propietario: {propiedad['Propietario']}",
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(m)
            folium_static(m)
        
        with tab3:
            st.markdown("""<h3 style='color: #1e3d59;'>📈 Estado de Fiscalización de las Propiedades</h3>""", unsafe_allow_html=True)
            
            # Mostrar estadísticas detalladas
            st.subheader("Análisis por Fiscalización DOM")
            fiscalizadas_count = {}
            for propiedad in propiedades['datos']:
                fiscalizacion_dom = propiedad['Fiscalización DOM']
                if fiscalizacion_dom in fiscalizadas_count:
                    fiscalizadas_count[fiscalizacion_dom] += 1
                else:
                    fiscalizadas_count[fiscalizacion_dom] = 1
            
            # Gráfico de torta para Fiscalización DOM
            fig1 = go.Figure(data=[go.Pie(
                labels=list(fiscalizadas_count.keys()),
                values=list(fiscalizadas_count.values()),
                hole=.3,
                textinfo='label+percent',
                marker=dict(colors=['#2ecc71', '#e74c3c', '#3498db'])
            )])
            fig1.update_layout(
                title='Distribución por Estado de Fiscalización',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Mostrar métricas para Fiscalización DOM
            st.subheader("Resumen de Fiscalización")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="CONSTRUCCION REGULARIZADA",
                    value=fiscalizadas_count.get('CONSTRUCCION REGULARIZADA', 0),
                    delta=f"{(fiscalizadas_count.get('CONSTRUCCION REGULARIZADA', 0) / len(propiedades['datos']) * 100):.1f}% del total" if len(propiedades['datos']) > 0 else "0%"
                )
            with col2:
                st.metric(
                    label="CONSTRUCCION IRREGULAR",
                    value=fiscalizadas_count.get('CONSTRUCCION IRREGULAR', 0),
                    delta=f"{(fiscalizadas_count.get('CONSTRUCCION IRREGULAR', 0) / len(propiedades['datos']) * 100):.1f}% del total" if len(propiedades['datos']) > 0 else "0%"
                )
            
            # Análisis de PATENTE COMERCIAL
            st.markdown("---")
            st.subheader("Análisis por Patente Comercial")
            if 'Patente Comercial' in propiedades['datos'][0]:
                patentes_count = {}
                for propiedad in propiedades['datos']:
                    patente_comercial = propiedad['Patente Comercial']
                    if patente_comercial in patentes_count:
                        patentes_count[patente_comercial] += 1
                    else:
                        patentes_count[patente_comercial] = 1
                
                # Gráfico de barras para Patente Comercial
                fig2 = go.Figure([
                    go.Bar(
                        x=list(patentes_count.keys()),
                        y=list(patentes_count.values()),
                        marker_color=['#3498db', '#2ecc71', '#e74c3c']
                    )
                ])
                fig2.update_layout(
                    title='Distribución por Estado de Patente Comercial',
                    xaxis_title='Estado de Patente',
                    yaxis_title='Cantidad de Propiedades',
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Mostrar métricas para Patente Comercial
                st.subheader("Resumen de Patentes")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="PATENTE AL DIA",
                        value=patentes_count.get('PATENTE AL DIA', 0),
                        delta=f"{(patentes_count.get('PATENTE AL DIA', 0) / len(propiedades['datos']) * 100):.1f}% del total" if len(propiedades['datos']) > 0 else "0%"
                    )
                with col2:
                    st.metric(
                        label="PATENTE MOROSA",
                        value=patentes_count.get('PATENTE MOROSA', 0),
                        delta=f"{(patentes_count.get('PATENTE MOROSA', 0) / len(propiedades['datos']) * 100):.1f}% del total" if len(propiedades['datos']) > 0 else "0%"
                    )
                with col3:
                    st.metric(
                        label="SIN PATENTE",
                        value=patentes_count.get('SIN PATENTE', 0),
                        delta=f"{(patentes_count.get('SIN PATENTE', 0) / len(propiedades['datos']) * 100):.1f}% del total" if len(propiedades['datos']) > 0 else "0%"
                    )
                
                # Análisis cruzado entre Fiscalización y Patente
                st.markdown("---")
                st.subheader("Relación entre Fiscalización y Patente Comercial")
                if not propiedades['datos'].empty:
                    cross_tab = {}
                    for propiedad in propiedades['datos']:
                        fiscalizacion_dom = propiedad['Fiscalización DOM']
                        patente_comercial = propiedad['Patente Comercial']
                        if fiscalizacion_dom in cross_tab:
                            if patente_comercial in cross_tab[fiscalizacion_dom]:
                                cross_tab[fiscalizacion_dom][patente_comercial] += 1
                            else:
                                cross_tab[fiscalizacion_dom][patente_comercial] = 1
                        else:
                            cross_tab[fiscalizacion_dom] = {patente_comercial: 1}
                    
                    st.write(cross_tab)
    else:
        st.info("No hay propiedades registradas.")

elif opcion == "Buscar Propiedades":
    st.markdown("""<h2>🔍 Buscar Propiedades</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Busque propiedades por RUT, Propietario, Dirección o ROL Propiedad</p>""", unsafe_allow_html=True)
    
    busqueda = st.text_input("Ingrese término de búsqueda (RUT, Propietario, Dirección, ROL Propiedad)")
    
    if busqueda:
        resultado = obtener_propiedades(filtros={'rut': busqueda, 'propietario': busqueda, 'direccion': busqueda, 'rol_propiedad': busqueda})
        
        if len(resultado['datos']) > 0:
            st.write(resultado['datos'])
        else:
            st.info("No se encontraron propiedades que coincidan con la búsqueda.")

elif opcion == "Exportar Datos":
    st.markdown("""<h2>📊 Exportar Datos</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Exporte los datos del catastro en formato Excel</p>""", unsafe_allow_html=True)
    
    propiedades = obtener_propiedades()
    
    if len(propiedades['datos']) > 0:
        # Exportar a Excel
        df = pd.DataFrame(propiedades['datos'])
        excel_file = df.to_excel(index=False)
        st.download_button(
            label="Descargar como Excel",
            data=excel_file,
            file_name="catastro_propiedades.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        # Mostrar botón para exportar resultados
        if not df.empty:
            csv = df.drop(columns=['Fotos']).to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Exportar resultados a CSV",
                data=csv,
                file_name='busqueda_propiedades.csv',
                mime='text/csv',
            )
    else:
        st.info("No hay datos para exportar.")

elif opcion == "Gestionar Fotos":
    st.markdown("""<h2>🖼️ Gestión de Fotos de Propiedades</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Agregue o visualice fotos de las propiedades</p>""", unsafe_allow_html=True)
    
    # Seleccionar propiedad
    propiedades = obtener_propiedades()
    
    if 'datos' in propiedades and propiedades['datos']:
        # Crear lista de propiedades para el selector
        propiedades_lista = [f"{propiedad['RUT']} - {propiedad['Propietario']} - {propiedad['Dirección']}" for propiedad in propiedades['datos']]
        
        propiedad_seleccionada = st.selectbox(
            "Seleccione una propiedad:",
            propiedades_lista,
            index=0
        )
        
        # Obtener el índice de la propiedad seleccionada
        idx = propiedades_lista.index(propiedad_seleccionada)
        propiedad = propiedades['datos'][idx]
        
        st.markdown("### Información de la Propiedad")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Propietario:** {propiedad['Propietario']}")
            st.write(f"**RUT:** {propiedad['RUT']}")
        with col2:
            st.write(f"**Dirección:** {propiedad['Dirección']}")
            st.write(f"**ROL Propiedad:** {propiedad['ROL Propiedad']}")
        
        st.markdown("---")
        st.markdown("### Fotos de la Propiedad")
        
        # Mostrar fotos existentes
        fotos = propiedad['Fotos'] if isinstance(propiedad['Fotos'], list) else []
        
        if fotos:
            st.markdown("**Fotos existentes:**")
            cols = st.columns(3)
            for i, foto in enumerate(fotos):
                with cols[i % 3]:
                    st.image(foto, use_column_width=True)
                    if st.button(f"Eliminar foto {i+1}", key=f"del_{i}"):
                        # Eliminar la foto
                        try:
                            os.remove(foto)
                            fotos.pop(i)
                            guardar_fotos(propiedad['id'], fotos)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar la foto: {e}")
        else:
            st.info("No hay fotos para esta propiedad.")
        
        # Subir nuevas fotos
        st.markdown("### Agregar Nuevas Fotos")
        uploaded_files = st.file_uploader(
            "Seleccione una o más fotos para esta propiedad",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Guardar Fotos"):
                nuevas_fotos = []
                for uploaded_file in uploaded_files:
                    try:
                        # Crear directorio de uploads si no existe
                        os.makedirs('uploads', exist_ok=True)
                        # Generar nombre de archivo único
                        timestamp = int(time.time())
                        file_extension = os.path.splitext(uploaded_file.name)[1]
                        file_name = f"{propiedad['RUT']}_{timestamp}{file_extension}"
                        file_path = os.path.join('uploads', file_name)
                        
                        # Guardar el archivo
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Agregar a la lista de nuevas fotos
                        nuevas_fotos.append(file_path)
                        
                    except Exception as e:
                        st.error(f"Error al procesar la foto {uploaded_file.name}: {e}")
                
                if nuevas_fotos:
                    # Obtener fotos existentes
                    fotos_existentes = propiedad.get('Fotos', [])
                    if not isinstance(fotos_existentes, list):
                        fotos_existentes = []
                    
                    # Combinar fotos existentes con nuevas
                    todas_las_fotos = fotos_existentes + nuevas_fotos
                    
                    # Guardar en la base de datos
                    if guardar_fotos(propiedad['id'], todas_las_fotos):
                        st.success(f"¡{len(nuevas_fotos)} fotos guardadas correctamente!")
                        st.rerun()
                    else:
                        st.error("Error al guardar las fotos en la base de datos.")
                else:
                    st.warning("No se pudo guardar ninguna foto.")
    else:
        st.info("No hay propiedades registradas para gestionar fotos.")
        