import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
import time
from datetime import datetime
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

# Estilos CSS personalizados para el menú - Tema Oscuro Moderno
st.markdown("""
<style>
    :root {
        --primary: #6c63ff;
        --primary-hover: #7d76ff;
        --bg-dark: #0f172a;
        --bg-darker: #0b1120;
        --text: #e2e8f0;
        --text-muted: #94a3b8;
        --card-bg: rgba(30, 41, 59, 0.7);
        --border: rgba(255, 255, 255, 0.1);
    }
    
    /* Estilo general del menú */
    .sidebar .sidebar-content {
        background: var(--bg-dark) !important;
        color: var(--text);
        border-right: 1px solid var(--border);
    }
    
    /* Estilo para los botones del menú */
    .menu-button {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .menu-button:hover {
        background: rgba(108, 99, 255, 0.1) !important;
        border-color: var(--primary) !important;
        transform: translateX(8px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .menu-button:active {
        transform: translateX(8px) scale(0.98) !important;
    }
    
    .menu-button[data-baseweb="button"] > div > div {
        justify-content: flex-start !important;
        gap: 12px;
    }
    
    /* Estilo para el botón activo */
    .menu-button[data-baseweb="button"][data-testid="baseButton-secondary"] {
        background: var(--primary) !important;
        color: white !important;
        font-weight: 500;
    }
    
    /* Estilo para los títulos */
    .sidebar .stMarkdown h3 {
        color: var(--primary);
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        position: relative;
        padding-bottom: 0.5rem;
    }
    
    .sidebar .stMarkdown h3::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 40px;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), transparent);
        border-radius: 3px;
    }
    
    /* Estilo para el pie de página */
    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        left: 1.5rem;
        right: 1.5rem;
        color: var(--text-muted);
        font-size: 0.75rem;
        text-align: center;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
    }
    
    /* Estilo para el logo */
    .logo-container {
        text-align: center;
        padding: 1.5rem 0;
        margin: 0 0 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .logo-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150%;
        height: 100%;
        background: radial-gradient(circle, rgba(108,99,255,0.1) 0%, rgba(0,0,0,0) 70%);
        z-index: 0;
    }
    
    .logo-container img {
        max-width: 70%;
        height: auto;
        border-radius: 12px;
        position: relative;
        z-index: 1;
        transition: all 0.3s ease;
        border: 1px solid var(--border);
    }
    
    .logo-container:hover img {
        transform: scale(1.03);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    
    /* Efecto de hover para los elementos del menú */
    .menu-item {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-darker);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-hover);
    }
    
    /* Efecto de brillo al pasar el cursor */
    .menu-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: 0.5s;
    }
    
    .menu-button:hover::before {
    }
</style>
""", unsafe_allow_html=True)

# Barra lateral para navegación
with st.sidebar:
    # Logo y título
    st.markdown('''
    <div class="logo-container">
        <img src="https://www.municipalidaddesantiago.cl/wp-content/uploads/2021/12/logo-municipalidad-santiago.png" 
             alt="Logo Municipalidad" 
             style="width: 100%; max-width: 180px;">
        <h3 style='color: #ffffff; margin: 10px 0 0 0;'>Catastro de Propiedades</h3>
        <p style='color: rgba(255, 255, 255, 0.7); font-size: 12px; margin: 5px 0 0 0;'>Comuna de Independencia</p>
    </div>
    <div class="menu-title">Menú Principal</div>
    ''', unsafe_allow_html=True)
    
    # Opciones del menú con iconos
    menu_items = [
        {"icon": "", "label": "Inicio", "key": "Inicio"},
        {"icon": "", "label": "Gestión de Propiedades", "key": "Gestión de Propiedades"},
        {"icon": "", "label": "Ver/Editar Propiedades", "key": "Ver/Editar Propiedades"},
        {"icon": "", "label": "Buscar Propiedades", "key": "Buscar Propiedades"},
        {"icon": "", "label": "Reportes", "key": "Reportes"},
        {"icon": "", "label": "Exportar Datos", "key": "Exportar Datos"},
        {"icon": "", "label": "Gestionar Fotos", "key": "Gestionar Fotos"}
    ]
    
    # Mostrar las opciones del menú
    for item in menu_items:
        # Determinar si la opción está activa
        is_active = st.session_state.menu_seleccionado == item["key"]
        
        # Estilo para el botón activo
        button_style = ""
        if is_active:
            button_style = """
                background-color: rgba(255, 255, 255, 0.2) !important;
                border-left: 3px solid #ff6b6b !important;
                font-weight: 600 !important;
            """
        
        # Crear el botón con el estilo correspondiente
            "description": "Página principal del sistema de catastro"
        },
        "Agregar Propiedad": {
            "icon": "📝", 
            "description": "Registrar una nueva propiedad en el sistema"
        },
        "Ver/Editar Propiedades": {
            "icon": "🏢", 
            "description": "Explorar y modificar propiedades existentes"
        },
        "Buscar Propiedades": {
            "icon": "🔍", 
            "description": "Búsqueda avanzada de propiedades por múltiples criterios"
        },
        "Gestionar Fotos": {
            "icon": "🖼️", 
            "description": "Administrar el archivo fotográfico de las propiedades"
        },
        "Exportar Datos": {
            "icon": "📊", 
            "description": "Generar reportes y exportar datos del catastro"
        }
    }
    
    # Inicializar estado del menú si no existe
    if 'menu_seleccionado' not in st.session_state:
        st.session_state.menu_seleccionado = "Inicio"
    
    # Variables para el estilo de los botones
    button_style = """
    <style>
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        .menu-title {
            text-align: center;
            margin-bottom: 1.5rem !important;
            color: #e2e8f0;
            font-size: 1.4rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            padding-bottom: 0.5rem;
        }
        .menu-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: linear-gradient(90deg, #6c63ff, #9f7aea);
            border-radius: 3px;
        }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    # Mostrar menú de navegación
    for opcion, datos in menu_opciones.items():
        if st.button(
            f"{datos['icon']} {opcion}",
            key=f"btn_{opcion}",
            help=datos["description"],
            use_container_width=True,
            type="primary" if st.session_state.menu_seleccionado == opcion else "secondary"
        ):
            st.session_state.menu_seleccionado = opcion
            st.rerun()
    
    # Espaciador
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Sección de información
    st.markdown("<h3>📌 Información</h3>", unsafe_allow_html=True)
    
    # Tarjeta de información
    st.markdown("""
    <div style="
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <p style="margin: 0; color: #e2e8f0; font-size: 0.9rem;">
            <span style="color: #6c63ff; font-weight: 600;">Sistema de Catastro</span><br>
            <span style="color: #94a3b8; font-size: 0.8rem;">Comuna de Independencia</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pie de página
    st.markdown("""
    <div class="sidebar-footer">
        <div style="margin-bottom: 0.5rem;">
            <span style="color: #6c63ff; font-weight: 500;">Versión 2.0.0</span>
        </div>
        <div style="color: #64748b; font-size: 0.75rem;">
            © 2025 Municipalidad de Independencia<br>
            <span style="font-size: 0.7rem; opacity: 0.8;">Todos los derechos reservados</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Variable para la opción seleccionada
    opcion = st.session_state.menu_seleccionado

# Contenido principal de la aplicación
if st.session_state.menu_seleccionado == "Ver/Editar Propiedades" or opcion == "Ver/Editar Propiedades":
    st.title("📋 Ver/Editar Propiedades")
    
    # Obtener todas las propiedades de la base de datos
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, propietario, rut, direccion, rol_propiedad, 
                       NULL as comuna, NULL as region, destino_sii
                FROM propiedades
                ORDER BY fecha_creacion DESC
            """)
            propiedades = cursor.fetchall()
            
            if propiedades:
                # Mostrar las propiedades en una tabla
                st.markdown("### Listado de Propiedades")
                
                # Crear un DataFrame para mostrar en la tabla
                import pandas as pd
                df = pd.DataFrame(propiedades, columns=["ID", "Propietario", "RUT", "Dirección", "Rol", "Comuna", "Región", "Destino SII"])
                
                # Mostrar la tabla con opciones de edición
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Propietario": "Propietario",
                        "RUT": "RUT",
                        "Dirección": "Dirección",
                        "Rol": "Rol",
                        "Comuna": "Comuna",
                        "Región": "Región",
                        "Destino SII": "Destino SII"
                    }
                )
                
                # Opción para editar una propiedad específica
                st.markdown("### Editar Propiedad")
                propiedad_id = st.selectbox(
                    "Seleccione una propiedad para editar:",
                    [f"{p[0]} - {p[1]} - {p[3]}" for p in propiedades],
                    index=None,
                    placeholder="Seleccione una propiedad"
                )
                
                if propiedad_id:
                    # Obtener el ID de la propiedad seleccionada
                    prop_id = int(propiedad_id.split(" - ")[0])
                    
                    # Obtener los datos actuales de la propiedad
                    cursor.execute("""
                        SELECT * FROM propiedades WHERE id = ?
                    """, (prop_id,))
                    propiedad = cursor.fetchone()
                    
                    if propiedad:
                        with st.form(f"form_editar_{prop_id}"):
                            st.write("### Editar Propiedad")
                            
                            # Mapear los campos de la base de datos a variables más legibles
                            campos = {
                                "propietario": st.text_input("Propietario", value=propiedad[1]),
                                "rut": st.text_input("RUT", value=propiedad[2]),
                                "direccion": st.text_input("Dirección", value=propiedad[3]),
                                "rol_propiedad": st.text_input("Rol de Propiedad", value=propiedad[4] if propiedad[4] else ""),
                                "destino_sii": st.text_input("Destino SII", value=propiedad[7] if propiedad[7] else ""),
                                "avaluo_total": st.number_input("Avalúo Total", value=float(propiedad[8]) if propiedad[8] else 0.0, min_value=0.0, step=1000.0),
                                "destino_dom": st.text_input("Destino DOM", value=propiedad[9] if propiedad[9] else ""),
                                "patente_comercial": st.text_input("Patente Comercial", value=propiedad[10] if propiedad[10] else ""),
                                "num_contacto": st.text_input("Número de Contacto", value=propiedad[11] if propiedad[11] else ""),
                                "coordenadas": st.text_input("Coordenadas", value=propiedad[12] if propiedad[12] else ""),
                                "fiscalizacion_dom": st.text_input("Fiscalización DOM", value=propiedad[13] if propiedad[13] else ""),
                                "m2_terreno": st.number_input("m² de Terreno", value=float(propiedad[14]) if propiedad[14] else 0.0, min_value=0.0, step=0.1),
                                "m2_construidos": st.number_input("m² Construidos", value=float(propiedad[15]) if propiedad[15] else 0.0, min_value=0.0, step=0.1),
                                "linea_construccion": st.text_input("Línea de Construcción", value=propiedad[16] if propiedad[16] else ""),
                                "ano_construccion": st.number_input("Año de Construcción", value=int(propiedad[17]) if propiedad[17] else datetime.now().year, min_value=1800, max_value=datetime.now().year),
                                "expediente_dom": st.text_input("Expediente DOM", value=propiedad[18] if propiedad[18] else ""),
                                "observaciones": st.text_area("Observaciones", value=propiedad[19] if propiedad[19] else "")
                            }
                            
                            # Botones de acción
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    try:
                                        # Actualizar la propiedad en la base de datos
                                        cursor.execute("""
                                            UPDATE propiedades 
                                            SET 
                                                propietario = ?, 
                                                rut = ?, 
                                                direccion = ?, 
                                                rol_propiedad = ?,
                                                destino_sii = ?,
                                                avaluo_total = ?,
                                                destino_dom = ?,
                                                patente_comercial = ?,
                                                num_contacto = ?,
                                                coordenadas = ?,
                                                fiscalizacion_dom = ?,
                                                m2_terreno = ?,
                                                m2_construidos = ?,
                                                linea_construccion = ?,
                                                ano_construccion = ?,
                                                expediente_dom = ?,
                                                observaciones = ?,
                                                fecha_actualizacion = CURRENT_TIMESTAMP
                                            WHERE id = ?
                                        """, (
                                            campos["propietario"],
                                            campos["rut"],
                                            campos["direccion"],
                                            campos["rol_propiedad"] if campos["rol_propiedad"] else None,
                                            campos["destino_sii"] if campos["destino_sii"] else None,
                                            campos["avaluo_total"],
                                            campos["destino_dom"] if campos["destino_dom"] else None,
                                            campos["patente_comercial"] if campos["patente_comercial"] else None,
                                            campos["num_contacto"] if campos["num_contacto"] else None,
                                            campos["coordenadas"] if campos["coordenadas"] else None,
                                            campos["fiscalizacion_dom"] if campos["fiscalizacion_dom"] else None,
                                            campos["m2_terreno"],
                                            campos["m2_construidos"],
                                            campos["linea_construccion"] if campos["linea_construccion"] else None,
                                            campos["ano_construccion"] if campos["ano_construccion"] else None,
                                            campos["expediente_dom"] if campos["expediente_dom"] else None,
                                            campos["observaciones"] if campos["observaciones"] else None,
                                            prop_id
                                        ))
                                        conn.commit()
                                        st.success("✅ Propiedad actualizada correctamente")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al actualizar la propiedad: {str(e)}")
                            
                            with col2:
                                if st.form_submit_button("🗑️ Eliminar Propiedad", type="secondary"):
                                    try:
                                        # Eliminar la propiedad de la base de datos
                                        cursor.execute("DELETE FROM propiedades WHERE id = ?", (prop_id,))
                                        conn.commit()
                                        st.success("🗑️ Propiedad eliminada correctamente")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al eliminar la propiedad: {str(e)}")
            else:
                st.info("No hay propiedades registradas aún.")
                
        except Exception as e:
            st.error(f"Error al obtener las propiedades: {str(e)}")
        finally:
            conn.close()
            
elif st.session_state.menu_seleccionado == "Buscar Propiedades" or opcion == "Buscar Propiedades":
    st.title("🔍 Buscar Propiedades")
    
    # Formulario de búsqueda
    with st.form("form_busqueda"):
        col1, col2 = st.columns(2)
        
        with col1:
            busqueda_rut = st.text_input("RUT del Propietario")
            busqueda_direccion = st.text_input("Dirección")
            busqueda_rol = st.text_input("Rol de Propiedad")
            
        with col2:
            busqueda_destino_sii = st.text_input("Destino SII")
            busqueda_patente = st.text_input("Patente Comercial")
        
        # Botones de búsqueda
        col1, col2, _ = st.columns([1, 1, 3])
        with col1:
            btn_buscar = st.form_submit_button("🔍 Buscar")
        with col2:
            btn_limpiar = st.form_submit_button("🧹 Limpiar Filtros")
    
    # Procesar búsqueda
    if btn_buscar or btn_limpiar:
        # Construir filtros
        filtros = {}
        if not btn_limpiar:  # Solo aplicar filtros si no se está limpiando
            if busqueda_rut:
                filtros["rut"] = f"%{busqueda_rut}%"
            if busqueda_direccion:
                filtros["direccion"] = f"%{busqueda_direccion}%"
            if busqueda_rol:
                filtros["rol_propiedad"] = f"%{busqueda_rol}%"
            if busqueda_destino_sii:
                filtros["destino_sii"] = f"%{busqueda_destino_sii}%"
            if busqueda_patente:
                filtros["patente_comercial"] = f"%{busqueda_patente}%"
        
        # Realizar la búsqueda
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Construir la consulta dinámicamente
                query = """
                    SELECT id, propietario, rut, direccion, rol_propiedad, destino_sii, 
                           patente_comercial, fecha_creacion
                    FROM propiedades
                """
                
                # Agregar condiciones WHERE si hay filtros
                conditions = []
                params = []
                
                for key, value in filtros.items():
                    conditions.append(f"{key} LIKE ?")
                    params.append(value)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                # Ordenar por fecha de creación descendente
                query += " ORDER BY fecha_creacion DESC"
                
                # Ejecutar la consulta
                cursor.execute(query, tuple(params))
                resultados = cursor.fetchall()
                
                # Mostrar resultados
                if resultados:
                    st.success(f"🔍 Se encontraron {len(resultados)} propiedades que coinciden con los criterios de búsqueda.")
                    
                    # Mostrar resultados en una tabla
                    df_resultados = pd.DataFrame(resultados, columns=[
                        "ID", "Propietario", "RUT", "Dirección", "Rol", "Destino SII", 
                        "Patente Comercial", "Fecha de Creación"
                    ])
                    
                    # Formatear columnas
                    if not df_resultados.empty:
                        df_resultados["Fecha de Creación"] = pd.to_datetime(df_resultados["Fecha de Creación"]).dt.strftime('%d/%m/%Y %H:%M')
                    
                    st.dataframe(
                        df_resultados,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "ID": st.column_config.NumberColumn("ID", width="small"),
                            "Propietario": "Propietario",
                            "RUT": "RUT",
                            "Dirección": "Dirección",
                            "Rol": "Rol",
                            "Destino SII": "Destino SII",
                            "Patente Comercial": "Patente",
                            "Fecha de Creación": "Fecha"
                        }
                    )
                    
                    # Opción para ver detalles de una propiedad
                    if len(resultados) == 1:
                        st.session_state.propiedad_seleccionada = resultados[0][0]
                        st.session_state.menu_seleccionado = "Ver/Editar Propiedades"
                        st.rerun()
                    elif len(resultados) > 1:
                        seleccion = st.selectbox(
                            "Seleccione una propiedad para ver detalles:",
                            [f"{r[0]} - {r[1]} - {r[3]}" for r in resultados],
                            index=None,
                            placeholder="Seleccione una propiedad"
                        )
                        
                        if seleccion:
                            prop_id = int(seleccion.split(" - ")[0])
                            st.session_state.propiedad_seleccionada = prop_id
                            st.session_state.menu_seleccionado = "Ver/Editar Propiedades"
                            st.rerun()
                
                else:
                    st.info("No se encontraron propiedades que coincidan con los criterios de búsqueda.")
                
            except Exception as e:
                st.error(f"Error al realizar la búsqueda: {str(e)}")
            finally:
                conn.close()
    
elif st.session_state.menu_seleccionado == "Inicio" or opcion == "Inicio":
    st.title("Bienvenido al Sistema de Catastro")
    
    # Tarjetas de acceso rápido
    st.markdown("### Acceso Rápido")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Agregar Nueva Propiedad", use_container_width=True, key="btn_agregar_inicio"):
            st.session_state.menu_seleccionado = "Gestión de Propiedades"
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Propiedades", use_container_width=True, key="btn_ver_inicio"):
            st.session_state.menu_seleccionado = "Gestión de Propiedades"
            st.rerun()
    
    with col3:
        if st.button("📊 Generar Informe", use_container_width=True, key="btn_informe_inicio"):
            st.session_state.menu_seleccionado = "Informes"
            st.rerun()
    
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
    
    # Botón de Atrás con diseño limpio
    if 'menu_seleccionado' in st.session_state and st.session_state.menu_seleccionado != "Inicio":
        # Estilos CSS para el botón
        st.markdown("""
            <style>
                .back-btn-clean {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    background: #ffffff;
                    color: #1e3d59;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    cursor: pointer;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    transition: all 0.2s ease;
                }
                .back-btn-clean:hover {
                    background: #f8f9fa;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                .back-btn-clean:active {
                    transform: translateY(0);
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                }
                .back-arrow {
                    font-size: 16px;
                    transition: transform 0.2s ease;
                }
                .back-btn-clean:hover .back-arrow {
                    transform: translateX(-2px);
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Estilos CSS para el botón de volver
        st.markdown("""
        <style>
            .floating-btn-container {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 1000;
            }
            .floating-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                background: linear-gradient(135deg, #6c63ff 0%, #8e85ff 100%);
                color: white !important;
                border: none;
                border-radius: 50px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
                transition: all 0.3s ease;
                text-decoration: none;
                border: 2px solid transparent;
            }
            .floating-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
                background: linear-gradient(135deg, #5b52e6 0%, #7d74ff 100%);
            }
            .floating-btn:active {
                transform: translateY(1px);
            }
            .floating-btn i {
                font-size: 18px;
                transition: transform 0.3s ease;
            }
            .floating-btn:hover i {
                transform: translateX(-3px);
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Incluir Font Awesome para el ícono
        st.markdown(
            """
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            """,
            unsafe_allow_html=True
        )
        
        # Crear un formulario para manejar el botón de volver
        with st.form(key='volver_form'):
            # Botón oculto que maneja la lógica de navegación
            if st.form_submit_button(
                " ",
                help="Volver al inicio",
                type="primary"
            ):
                st.session_state.menu_seleccionado = "Inicio"
                st.rerun()
        
        # Botón flotante personalizado que activa el formulario
        st.markdown(
            """
            <style>
                .floating-btn-container {
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    z-index: 1000;
                }
                .floating-btn {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    background: linear-gradient(135deg, #6c63ff 0%, #8e85ff 100%);
                    color: white !important;
                    border: none;
                    border-radius: 50px;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
                    transition: all 0.3s ease;
                    text-decoration: none;
                    border: 2px solid transparent;
                }
                .floating-btn:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
                    background: linear-gradient(135deg, #5b52e6 0%, #7d74ff 100%);
                }
                .floating-btn:active {
                    transform: translateY(1px);
                }
                .floating-btn i {
                    font-size: 18px;
                    transition: transform 0.3s ease;
                }
                .floating-btn:hover i {
                    transform: translateX(-3px);
                }
                /* Ocultar el botón del formulario */
                div[data-testid="stForm"] > div:first-child {
                    display: none;
                }
            </style>
            
            <div class="floating-btn-container">
                <button class="floating-btn" onclick="document.querySelector('div[data-testid=\'stForm\'] button').click()">
                    <i class="fas fa-home"></i>
                    <span>Volver al Inicio</span>
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Línea separadora
    st.markdown("---")


# El menú de navegación principal ya está definido al inicio del archivo
# Esta sección se ha eliminado para evitar duplicación de menús

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

# Sección de gestión de propiedades
if st.session_state.menu_seleccionado == "Gestión de Propiedades":
    # Crear pestañas
    tab1, tab2 = st.tabs(["📋 Lista de Propiedades", "➕ Agregar Nueva"])
    
    # Contenido de la pestaña de lista de propiedades
    with tab1:
        st.markdown("""<h3>📋 Lista de Propiedades</h3>""", unsafe_allow_html=True)
        # Filtros de búsqueda
        with st.expander("🔍 Filtros de Búsqueda", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                filtro_rut = st.text_input("RUT Propietario")
                filtro_direccion = st.text_input("Dirección")
            with col2:
                filtro_rol = st.text_input("ROL Propiedad")
                filtro_destino = st.selectbox("Destino SII", [""] + ["Habitacional", "Comercial", "Industrial", "Otros"])
    
    # Contenido de la pestaña de agregar nueva propiedad
    with tab2:
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
                            st.error("❌ Error al guardar la propiedad. Por favor intente nuevamente.")

# Sección de gestión de propiedades
if st.session_state.menu_seleccionado == "Gestión de Propiedades":
    # Crear pestañas
    tab1, tab2 = st.tabs(["📋 Lista de Propiedades", "➕ Agregar Nueva"])
    
    # Contenido de la pestaña de lista de propiedades
    with tab1:
        st.markdown("""<h3>📋 Lista de Propiedades</h3>""", unsafe_allow_html=True)
        # Filtros de búsqueda
        with st.expander("🔍 Filtros de Búsqueda", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                filtro_rut = st.text_input("RUT Propietario", key="filtro_rut_lista")
                filtro_direccion = st.text_input("Dirección", key="filtro_direccion_lista")
            with col2:
                filtro_rol = st.text_input("ROL Propiedad", key="filtro_rol_lista")
                filtro_destino = st.selectbox(
                    "Destino SII", 
                    [""] + ["Habitacional", "Comercial", "Industrial", "Otros"],
                    key="filtro_destino_lista"
                )
        
        # Aplicar filtros
        filtros = {}
        if filtro_rut: filtros['rut'] = filtro_rut
        if filtro_direccion: filtros['direccion'] = filtro_direccion
        if filtro_rol: filtros['rol_propiedad'] = filtro_rol
        if filtro_destino: filtros['destino_sii'] = filtro_destino
        
        # Obtener propiedades filtradas
        resultado = obtener_propiedades(filtros=filtros)
        
        if resultado['total'] > 0:
            # Mostrar tabla de propiedades
            st.dataframe(resultado['datos'])
        else:
            st.info("No se encontraron propiedades que coincidan con los filtros.")
    
    # Contenido de la pestaña de agregar propiedad
    with tab2:
        st.markdown("""
            <div style='background-color:#f8f9fa; padding:20px; border-radius:10px; margin-bottom:30px;'>
                <h2 style='color:#1e3d59; margin:0;'>📝 Agregar Nueva Propiedad</h2>
                <p style='color:#666; margin:5px 0 0 0;'>Complete el formulario con los datos de la propiedad</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("formulario_propiedad_agregar"):
            # Sección 1: Información Básica
            with st.expander("📋 Información Básica", expanded=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    rut = st.text_input("RUT del Propietario *", help="Formato: 12345678-9", key="rut_propietario_agregar")
                    propietario = st.text_input("Nombre del Propietario *", key="nombre_propietario_agregar")
                    num_contacto = st.text_input("N° de contacto *", help="Número de teléfono de contacto", key="num_contacto_agregar")
                    direccion = st.text_area("Dirección *", height=70, key="direccion_agregar")
            
            # Sección 2: Detalles de la Propiedad
            with st.expander("🏠 Detalles de la Propiedad", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    rol = st.text_input("ROL Propiedad *", key="rol_propiedad_agregar")
                    avaluo = st.number_input("Avalúo Total *", min_value=0, step=1000, format="%d", key="avaluo_total_agregar")
                    m2_terreno = st.number_input("M² Terreno *", min_value=0.0, step=0.01, key="m2_terreno_agregar")
                    m2_construidos = st.number_input("M² Construidos *", min_value=0.0, step=0.01, key="m2_construidos_agregar")
                    
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
                    help="Ingrese las coordenadas en formato: latitud, longitud",
                    key="coordenadas_agregar"
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
                observaciones = st.text_area("Ingrese cualquier observación adicional", height=100, key="observaciones_agregar")
            
            # Botón de envío
            st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "💾 Guardar Propiedad", 
                    use_container_width=True,
                    type="primary",
                    key="guardar_propiedad"
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
                            'Fiscalización DOM': fiscalizacion_dom,
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
                            st.error("❌ Error al guardar la propiedad. Por favor intente nuevamente.")
            
            # Botón de envío
            submitted = st.form_submit_button("Guardar Propiedad", key="guardar_propiedad")
            if submitted:
                if not all([rut, propietario, direccion, rol_propiedad]):
                    st.error("Por favor complete todos los campos obligatorios.")
                else:
                    # Crear diccionario con los datos de la propiedad
                    nueva_propiedad = {
                        'rut': rut,
                        'propietario': propietario,
                        'direccion': direccion,
                        'rol_propiedad': rol_propiedad,
                        'avaluo_total': avaluo,
                        'm2_terreno': m2_terreno,
                        'm2_construido': m2_construido,
                        'destino_sii': destino_sii,
                        'coordenadas': f"{latitud},{longitud}" if latitud and longitud else None,
                        'fiscalizacion_dom': fiscalizacion_dom
                    }
                    
                    # Guardar la propiedad
                    propiedad_id = guardar_propiedad(nueva_propiedad)
                    if propiedad_id:
                        st.success("✅ Propiedad guardada exitosamente!")
                    else:
                        st.error("❌ Error al guardar la propiedad. Por favor intente nuevamente.")
    
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

