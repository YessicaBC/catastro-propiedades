import os
import sys
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)  # Cambiar al directorio del script

# Agregar el directorio actual al path
sys.path.insert(0, str(BASE_DIR))

# Ahora importamos los demás módulos
import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium
import folium.plugins
import plotly.graph_objects as go
import time
import pandas as pd
from datetime import datetime
import json
import sqlite3
from sqlite3 import Error
import io

# Importar funciones de la base de datos
try:
    # Intentar importación estándar
    from db_utils import init_db, get_db_connection
except ImportError as e:
    st.error(f"Error al importar db_utils: {e}")
    st.stop()

# Inicializar la base de datos al inicio
if not init_db():
    st.error("No se pudo inicializar la base de datos. Por favor, verifica los permisos del directorio.")
    st.stop()

# Inicializar estado de la sesión
if 'opcion_seleccionada' not in st.session_state:
    st.session_state.opcion_seleccionada = "🏠 Inicio"
    # Inicializar estados de los inputs
    st.session_state['rut_input'] = ""
    st.session_state['propietario_input'] = ""
    st.session_state['num_contacto_input'] = ""
    st.session_state['direccion_input'] = ""
    st.session_state['rol_input'] = ""
    st.session_state['coordenadas_input'] = ""
    st.session_state['map_center'] = [-33.4172, -70.6506]
    st.session_state['marker_position'] = None

# Configuración de la página
st.set_page_config(
    page_title="Catastro Comunal de Independencia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS unificados
st.markdown("""
    <style>
        /* Estilos generales */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Títulos y encabezados */
        h1, h2, h3, h4, h5, h6 {
            color: #1e3d59;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 2.25rem;
            font-weight: 700;
            border-bottom: 2px solid #f0f2f6;
            padding-bottom: 0.5rem;
        }
        
        h2 {
            font-size: 1.75rem;
            font-weight: 600;
            margin-top: 1.5rem;
        }
        
        h3 {
            font-size: 1.5rem;
            font-weight: 500;
            color: #2c5282;
        }
        
        /* Subtítulos */
        .subheader {
            color: #4a5568;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }
        
        /* Tarjetas y contenedores */
        .card {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        /* Botones */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            padding: 0.5rem 1.25rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button:focus {
            box-shadow: 0 0 0 0.2rem rgba(30, 136, 229, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        }
        
        /* Formularios y campos de entrada */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > input[type="number"],
        .stSelectbox > div > div > div {
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            padding: 0.5rem 0.75rem;
        }
        
        .stTextInput > label,
        .stTextArea > label,
        .stNumberInput > label,
        .stSelectbox > label,
        .stDateInput > label,
        .stFileUploader > label {
            font-weight: 500;
            color: #2d3748;
            margin-bottom: 0.25rem;
        }
        
        /* Pestañas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            margin-bottom: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1.25rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1e88e5;
            color: white !important;
        }
        
        /* Mensajes de estado */
        .stAlert {
            border-radius: 8px;
        }
        
        .stAlert [data-testid="stMarkdownContainer"] {
            font-size: 0.95rem;
        }
        
        /* Barra lateral */
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            padding: 1.5rem 1rem;
        }
        
        [data-testid="stSidebarNav"] {
            margin-top: 2rem;
        }
        
        /* Galería de fotos */
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .gallery-item {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .gallery-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0,0.15);
        }
        
        /* Modal de imagen */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            max-width: 90%;
            max-height: 90%;
            margin: auto;
            display: block;
        }
        
        .close {
            position: absolute;
            top: 20px;
            right: 30px;
            color: #fff;
            font-size: 2rem;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s ease;
        }
        
        .close:hover {
            color: #ff6b6b;
        }
    </style>
""", unsafe_allow_html=True)

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
    """Guarda o actualiza una propiedad en la base de datos"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Verificar si la propiedad ya existe (usando RUT como identificador único)
            rut = propiedad.get('RUT', '')
            cursor.execute('SELECT id FROM propiedades WHERE rut = ?', (rut,))
            propiedad_existente = cursor.fetchone()
            
            if propiedad_existente:
                # Actualizar propiedad existente
                propiedad_id = propiedad_existente[0]
                cursor.execute('''
                UPDATE propiedades SET
                    propietario = ?,
                    direccion = ?,
                    rol_propiedad = ?,
                    avaluo_total = ?,
                    destino_sii = ?,
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
                WHERE rut = ?
                ''', (
                    propiedad.get('Propietario', ''), 
                    propiedad.get('Dirección', ''),
                    propiedad.get('ROL Propiedad', ''), 
                    propiedad.get('Avalúo Total', 0),
                    propiedad.get('Destino SII', ''),
                    propiedad.get('Destino DOM', ''), 
                    propiedad.get('Patente Comercial', ''), 
                    propiedad.get('N° de contacto', ''),
                    propiedad.get('Coordenadas', ''), 
                    propiedad.get('Fiscalización DOM', ''), 
                    propiedad.get('M2 Terreno', 0),
                    propiedad.get('M2 Construidos', 0), 
                    propiedad.get('Línea de Construcción', ''),
                    propiedad.get('Año de Construcción', ''), 
                    propiedad.get('Expediente DOM', ''), 
                    propiedad.get('Observaciones', ''),
                    rut
                ))
            else:
                # Insertar nueva propiedad
                cursor.execute('''
                INSERT INTO propiedades (
                    rut, propietario, direccion, rol_propiedad, avaluo_total,
                    destino_sii, destino_dom, patente_comercial, num_contacto,
                    coordenadas, fiscalizacion_dom, m2_terreno, m2_construidos,
                    linea_construccion, ano_construccion, expediente_dom, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rut,
                    propiedad.get('Propietario', ''), 
                    propiedad.get('Dirección', ''),
                    propiedad.get('ROL Propiedad', ''), 
                    propiedad.get('Avalúo Total', 0),
                    propiedad.get('Destino SII', ''),
                    propiedad.get('Destino DOM', ''), 
                    propiedad.get('Patente Comercial', ''), 
                    propiedad.get('N° de contacto', ''),
                    propiedad.get('Coordenadas', ''), 
                    propiedad.get('Fiscalización DOM', ''), 
                    propiedad.get('M2 Terreno', 0),
                    propiedad.get('M2 Construidos', 0), 
                    propiedad.get('Línea de Construcción', ''),
                    propiedad.get('Año de Construcción', ''), 
                    propiedad.get('Expediente DOM', ''), 
                    propiedad.get('Observaciones', '')
                ))
                propiedad_id = cursor.lastrowid
            
            conn.commit()
            return propiedad_id
            
        except Error as e:
            st.error(f"Error al guardar la propiedad: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
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

def obtener_total_propiedades():
    """Obtiene el número total de propiedades registradas"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM propiedades')
            total = cursor.fetchone()[0]
            return total
        except sqlite3.Error as e:
            st.error(f"Error al obtener el total de propiedades: {e}")
            return 0
        finally:
            conn.close()
    return 0

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
                fotos = [foto[0] for foto in cursor.fetchall()]
                propiedad['Fotos'] = fotos
                # Agregar miniatura (primera foto) si existe
                propiedad['Miniatura'] = fotos[0] if fotos else None
            
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

# Agregar manejador para eliminar fotos
if 'delete_photo' in st.query_params and st.query_params['delete_photo'] == 'true':
    if 'propiedad_id' in st.query_params and 'foto_index' in st.query_params:
        try:
            propiedad_id = st.query_params['propiedad_id']
            foto_index = int(st.query_params['foto_index'])
            
            # Obtener la propiedad
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, fotos FROM propiedades WHERE id = ?', (propiedad_id,))
            propiedad = cursor.fetchone()
            
            if propiedad:
                fotos = json.loads(propiedad['fotos']) if propiedad['fotos'] else []
                
                if 0 <= foto_index < len(fotos):
                    # Eliminar el archivo de la foto
                    try:
                        os.remove(fotos[foto_index])
                    except Exception as e:
                        st.error(f"Error al eliminar el archivo: {e}")
                    
                    # Eliminar la referencia de la base de datos
                    fotos.pop(foto_index)
                    cursor.execute('UPDATE propiedades SET fotos = ? WHERE id = ?', 
                                 (json.dumps(fotos), propiedad_id))
                    conn.commit()
                    st.success("Foto eliminada correctamente")
                else:
                    st.error("Índice de foto no válido")
            else:
                st.error("Propiedad no encontrada")
                
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")
        finally:
            conn.close()

# Inicializar la base de datos al inicio
if 'db_initialized' not in st.session_state:
    if init_db():
        st.session_state.db_initialized = True
    else:
        st.error("No se pudo inicializar la base de datos. La aplicación podría no funcionar correctamente.")

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

# Función para crear el mapa
def crear_mapa(coordenadas=None, zoom_start=13):
    """Crea un mapa centrado en las coordenadas dadas o en Independencia por defecto"""
    # Coordenadas por defecto: Comuna de Independencia
    default_coords = [-33.4172, -70.6506]
    
    if coordenadas:
        location = coordenadas
    else:
        location = default_coords
    
    m = folium.Map(location=location, zoom_start=zoom_start, tiles='OpenStreetMap')
    return m

# Menú de navegación
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #1e3d59; margin-bottom: 0.5rem;'>Menú Principal</h2>
            <div style='height: 3px; background: linear-gradient(90deg, #1e88e5, #64b5f6); margin: 0 auto 1.5rem; width: 50%; border-radius: 3px;'></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Opciones del menú con sus respectivos íconos
    opciones = [
        ("🏠", "Inicio"),
        ("📝", "Agregar Propiedad"),
        ("📋", "Ver/Editar Propiedades"),
        ("🔍", "Buscar Propiedades"),
        ("🖼️", "Gestionar Fotos"),
        ("📊", "Exportar Datos")
    ]
    
    # Mostrar las opciones como botones
    for icono, nombre in opciones:
        opcion = f"{icono} {nombre}"
        if st.button(opcion, key=f"menu_{nombre}", use_container_width=True):
            st.session_state.opcion_seleccionada = opcion
    
    # Usar el valor de la sesión
    opcion_seleccionada = st.session_state.opcion_seleccionada
    
    # Obtener solo el nombre de la opción seleccionada (sin el ícono)
    opcion = next((nombre for icono, nombre in opciones if icono in opcion_seleccionada), opcion_seleccionada)

# Contenido principal basado en la opción seleccionada
if opcion == "Inicio":
    # Contenedor principal con padding
    with st.container():
        # Título principal con ícono
        st.markdown("""
            <div style='width: 100%; text-align: center; margin: 0; padding: 1rem 0.5rem;'>
                <div style='color: #1e3d59; font-size: 1.8rem; font-weight: 600; white-space: nowrap; overflow: visible;'>
                    🏘️ Bienvenido al Catastro Comunal de Independencia
                </div>
                <div style='height: 4px; background: linear-gradient(90deg, #1e88e5, #64b5f6); margin: 1rem auto 0; width: 150px; border-radius: 2px;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Subtítulo descriptivo
        st.markdown("""
            <div style='text-align: center; margin: 0 auto 2rem; max-width: 800px; padding: 0 1rem;'>
                <p style='color: #4a4a4a; font-size: 1.05rem; line-height: 1.6; margin: 0;'>
                    Sistema de gestión de propiedades de la comuna de Independencia. 
                    Registre, consulte y administre la información catastral de manera eficiente.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Crear y mostrar el mapa
        m = crear_mapa(zoom_start=14)
        
        # Agregar marcador para el municipio
        folium.Marker(
            [-33.4172, -70.6506],
            popup='<b>Municipalidad de Independencia</b><br>Av. Independencia 405',
            tooltip='Municipalidad',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        
        # Agregar algunos puntos de referencia importantes
        puntos_interes = [
            {"nombre": "Hospital San José", "coords": [-33.4231, -70.6534]},
            {"nombre": "Plaza Chacabuco", "coords": [-33.4165, -70.6617]},
            {"nombre": "Estación Hospitales", "coords": [-33.4262, -70.6535]},
            {"nombre": "Parque Los Reyes", "coords": [-33.4250, -70.6770]},
            {"nombre": "Mall Barrio Independencia", "coords": [-33.4190, -70.6668]}
        ]
        
        for punto in puntos_interes:
            folium.Marker(
                punto["coords"],
                popup=f'<b>{punto["nombre"]}</b>',
                tooltip=punto["nombre"],
                icon=folium.Icon(color='green', icon='map-marker')
            ).add_to(m)
        
        # Agregar capa de polígono de la comuna (coordenadas aproximadas)
        comuna_coords = [
            [-33.4033, -70.6650],
            [-33.4035, -70.6450],
            [-33.4230, -70.6350],
            [-33.4380, -70.6450],
            [-33.4380, -70.6850],
            [-33.4033, -70.6650]
        ]
        
        folium.Polygon(
            locations=comuna_coords,
            color='#3186cc',
            weight=2,
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.2,
            popup='Comuna de Independencia'
        ).add_to(m)
        
        # Agregar control de capas
        folium.LayerControl().add_to(m)
        
        # Contenedor principal para el contenido de la página de inicio
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Sección de estadísticas y mapa
        col1, col2 = st.columns([1, 2.5], gap="large")
        
        with col1:
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            total_propiedades = obtener_total_propiedades()
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1e88e5, #64b5f6);
                    padding: 1.75rem 1.5rem;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                '>
                    <h3 style='margin: 0 0 12px 0; font-size: 1.1rem; font-weight: 500; color: rgba(255, 255, 255, 0.95);'>
                        Propiedades Registradas
                    </h3>
                    <p style='font-size: 2.75rem; font-weight: 700; margin: 0; line-height: 1.2;'>{total_propiedades}</p>
                    <p style='font-size: 0.9rem; margin: 8px 0 0 0; opacity: 0.9;'>
                        en el sistema catastral
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Tarjeta para el mapa con sombra y borde sutil
            st.markdown("""
                <div style='
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e0e0e0;
                    margin-bottom: 1.5rem;
                '>
            """, unsafe_allow_html=True)
            
            # Mostrar el mapa
            folium_static(m, width=800, height=500)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Espaciado final
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)


    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #1e3d59; margin-bottom: 0.5rem;'>Menú Principal</h2>
            <div style='height: 3px; background: linear-gradient(90deg, #1e88e5, #64b5f6); margin: 0 auto 1.5rem; width: 50%; border-radius: 3px;'></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Opciones del menú con sus respectivos íconos
    opciones = [
        ("🏠", "Inicio"),
        ("📝", "Agregar Propiedad"),
        ("📋", "Ver/Editar Propiedades"),
        ("🔍", "Buscar Propiedades"),
        ("🖼️", "Gestionar Fotos"),
        ("📊", "Exportar Datos")
    ]
    
    # Obtener solo el nombre de la opción seleccionada (sin el ícono)
    opcion = next((nombre for icono, nombre in opciones if icono in opcion_seleccionada), opcion_seleccionada)
    
    # Pie de página del menú
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <p style='font-size: 0.8rem; color: #666; margin-bottom: 0.5rem;'>Sistema de Catastro Municipal</p>
            <p style='font-size: 0.7rem; color: #999;'>Versión 1.0.0</p>
        </div>
    """, unsafe_allow_html=True)

def parse_coordenadas(coord_str):
    """Convierte string de coordenadas a tupla de flotantes (lat, lon)"""
    try:
        if not coord_str or not isinstance(coord_str, str):
            return None
        
        # Eliminar paréntesis y espacios si existen
        coord_str = coord_str.strip('() ').replace(' ', '')
        
        # Dividir por coma
        if ',' in coord_str:
            lat, lon = coord_str.split(',', 1)
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

# Estilos CSS personalizados para validación
st.markdown("""
    <style>
        .valid-field {
            border-left: 4px solid #4CAF50 !important;
        }
        .invalid-field {
            border-left: 4px solid #f44336 !important;
        }
        .field-container {
            position: relative;
            margin-bottom: 1rem;
        }
        .field-icon {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.2em;
        }
        .valid-icon {
            color: #4CAF50;
        }
        .invalid-icon {
            color: #f44336;
        }
        .required-field::after {
            content: " *";
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

if opcion == "Agregar Propiedad":
    st.markdown("""
        <div class='card'>
            <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                <span style='font-size: 2rem; margin-right: 0.75rem;'>📝</span>
                <div>
                    <h2 style='margin: 0;'>Agregar Nueva Propiedad</h2>
                    <p class='subheader' style='margin: 0.25rem 0 0 0;'>Complete el formulario con los datos de la propiedad</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("formulario_propiedad"):
        # Sección 1: Información Básica
        with st.expander("📋 Información Básica", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            # Columna 1
            with col1:
                # Validación de RUT en tiempo real
                rut_container = st.container()
                rut = rut_container.text_input("RUT Propietario", key="rut_input", help="Formato: 12345678-9")
                if rut:
                    is_rut_valid = validar_rut(rut)
                    rut_container.markdown(
                        f"""
                        <div class='field-icon'>{'✅' if is_rut_valid else '❌'}</div>
                        <style>
                            div[data-testid="stTextInput"]:has(> div > input[value="{rut}"]) > div > div > div > input {{
                                {'border-left: 4px solid #4CAF50 !important;' if is_rut_valid else 'border-left: 4px solid #f44336 !important;'}
                                padding-left: 8px !important;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    if not is_rut_valid:
                        rut_container.warning("Formato de RUT inválido. Use: 12345678-9")
                
                # Campo de propietario con validación
                propietario_container = st.container()
                propietario = propietario_container.text_input("Propietario", key="propietario_input")
                if propietario:
                    propietario_container.markdown(
                        f"""
                        <div class='field-icon'>{'✅' if propietario.strip() else '❌'}</div>
                        <style>
                            div[data-testid="stTextInput"]:has(> div > input[value="{propietario}"]) > div > div > div > input {{
                                {'border-left: 4px solid #4CAF50 !important;' if propietario.strip() else 'border-left: 4px solid #f44336 !important;'}
                                padding-left: 8px !important;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
            
                # Campo de número de contacto con validación
                num_contacto_container = st.container()
                num_contacto = num_contacto_container.text_input("N° de contacto", key="num_contacto_input", help="Número de teléfono de contacto")
                if num_contacto:
                    num_contacto_container.markdown(
                        f"""
                        <div class='field-icon'>{'✅' if num_contacto.strip() else '❌'}</div>
                        <style>
                            div[data-testid="stTextInput"]:has(> div > input[value="{num_contacto}"]) > div > div > div > input {{
                                {'border-left: 4px solid #4CAF50 !important;' if num_contacto.strip() else 'border-left: 4px solid #f44336 !important;'}
                                padding-left: 8px !important;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
            
                # Campo de dirección con validación
                direccion_container = st.container()
                direccion = direccion_container.text_area("Dirección", key="direccion_input", height=70)
                if direccion:
                    direccion_container.markdown(
                        f"""
                        <style>
                            div[data-testid="stTextArea"]:has(> label[data-testid="stWidgetLabel"]:contains("Dirección")) > div > div > textarea {{
                                {'border-left: 4px solid #4CAF50 !important;' if direccion.strip() else 'border-left: 4px solid #f44336 !important;'}
                                padding-left: 8px !important;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    if direccion.strip():
                        direccion_container.markdown(
                            "<div style='text-align: right;'><span style='color: #4CAF50;'>✓ Válido</span></div>",
                            unsafe_allow_html=True
                        )
                    else:
                        direccion_container.markdown(
                            "<div style='text-align: right;'><span style='color: #f44336;'>Campo obligatorio</span></div>",
                            unsafe_allow_html=True
                        )
        
        # Sección 2: Detalles de la Propiedad
        with st.expander("🏠 Detalles de la Propiedad", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Campo ROL con validación
                rol_container = st.container()
                rol = rol_container.text_input("ROL Propiedad", key="rol_input")
                if rol:
                    rol_container.markdown(
                        f"""
                        <div class='field-icon'>{'✅' if rol.strip() else '❌'}</div>
                        <style>
                            div[data-testid="stTextInput"]:has(> div > input[value="{rol}"]) > div > div > div > input {{
                                {'border-left: 4px solid #4CAF50 !important;' if rol.strip() else 'border-left: 4px solid #f44336 !important;'}
                                padding-left: 8px !important;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Campo Avalúo con validación
                avaluo_container = st.container()
                avaluo = avaluo_container.number_input("Avalúo Total", min_value=0, step=1000, format="%d", key="avaluo_input")
                avaluo_container.markdown(
                    f"""
                    <style>
                        div[data-testid="stNumberInput"]:has(> div > label:contains("Avalúo Total")) > div > div > input {{
                            {'border-left: 4px solid #4CAF50 !important;' if avaluo > 0 else 'border-left: 4px solid #f44336 !important;'}
                            padding-left: 8px !important;
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # Campo M² Terreno con validación
                m2_terreno_container = st.container()
                m2_terreno = m2_terreno_container.number_input("M² Terreno", min_value=0.0, step=0.01, key="m2_terreno_input")
                m2_terreno_container.markdown(
                    f"""
                    <style>
                        div[data-testid="stNumberInput"]:has(> div > label:contains("M² Terreno")) > div > div > input {{
                            {'border-left: 4px solid #4CAF50 !important;' if m2_terreno > 0 else 'border-left: 4px solid #f44336 !important;'}
                            padding-left: 8px !important;
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # Campo M² Construidos con validación
                m2_construidos_container = st.container()
                m2_construidos = m2_construidos_container.number_input("M² Construidos", min_value=0.0, step=0.01, key="m2_construidos_input")
                m2_construidos_container.markdown(
                    f"""
                    <style>
                        div[data-testid="stNumberInput"]:has(> div > label:contains("M² Construidos")) > div > div > input {{
                            {'border-left: 4px solid #4CAF50 !important;' if m2_construidos > 0 else 'border-left: 4px solid #f44336 !important;'}
                            padding-left: 8px !important;
                        }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
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
            # Usar columnas para organizar la entrada de coordenadas y el botón
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Campo de entrada para coordenadas manuales
                coordenadas_input = st.text_input(
                    "Coordenadas (Lat, Long)", 
                    key="coordenadas_input",
                    placeholder="Ej: -33.4172, -70.6506",
                    help="Ingrese las coordenadas manualmente o seleccione una ubicación en el mapa"
                )
            
            with col2:
                # Botón para centrar el mapa en la ubicación actual
                st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
                buscar_mapa = st.form_submit_button("🔍 Buscar en mapa", use_container_width=True, type="secondary")
                if buscar_mapa and coordenadas_input:
                    coords = parse_coordenadas(coordenadas_input)
                    if coords:
                        st.session_state['map_center'] = coords
                        st.session_state['marker_position'] = coords
                        st.rerun()
            
            # Inicializar el estado de la sesión para el mapa si no existe
            if 'map_center' not in st.session_state:
                st.session_state['map_center'] = [-33.4172, -70.6506]  # Coordenadas por defecto de Independencia
            if 'marker_position' not in st.session_state:
                st.session_state['marker_position'] = None
            
            # Crear el mapa interactivo
            m = folium.Map(location=st.session_state['map_center'], zoom_start=15)
            
            # Añadir marcador arrastrable si hay una posición guardada
            if st.session_state['marker_position']:
                folium.Marker(
                    st.session_state['marker_position'],
                    popup="Ubicación seleccionada",
                    icon=folium.Icon(color='red', icon='info-sign'),
                    draggable=True
                ).add_to(m)
            
            # Añadir control de capa para cambiar el tipo de mapa
            folium.TileLayer(
                'openstreetmap',
                name='OpenStreetMap',
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            ).add_to(m)
            
            folium.TileLayer(
                'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.{ext}',
                name='Stamen Terrain',
                attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                ext='png'
            ).add_to(m)
            
            folium.TileLayer(
                'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}',
                name='Stamen Toner',
                attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
                ext='png'
            ).add_to(m)
            
            folium.LayerControl().add_to(m)
            
            # Añadir control de pantalla completa
            folium.plugins.Fullscreen(
                position="topright",
                title="Pantalla completa",
                title_cancel="Salir de pantalla completa",
                force_separate_button=True
            ).add_to(m)
            
            # Añadir control de geolocalización
            folium.plugins.LocateControl(
                position="topright",
                draw_marker=True,
                locate_options={"enableHighAccuracy": True, "timeout": 10000},
                strings={"title": "Mi ubicación"}
            ).add_to(m)
            
            # Mostrar el mapa
            output = st_folium(m, width=700, height=400, key="mapa_interactivo")
            
            # Manejar clics en el mapa
            if output.get("last_clicked"):
                st.session_state['marker_position'] = [output["last_clicked"]["lat"], output["last_clicked"]["lng"]]
                st.session_state['map_center'] = st.session_state['marker_position']
                st.session_state['last_clicked'] = output["last_clicked"]
                st.rerun()
            
            # Actualizar el campo de coordenadas con la posición del marcador
            # Inicializar coordenadas con valor predeterminado
            coordenadas = ""
            
            if st.session_state.get('marker_position'):
                coordenadas = f"{st.session_state['marker_position'][0]}, {st.session_state['marker_position'][1]}"
                st.session_state['coordenadas_input'] = coordenadas
                st.markdown(f"**Ubicación seleccionada:** {st.session_state['marker_position'][0]:.6f}, {st.session_state['marker_position'][1]:.6f}")
            else:
                # Si no hay marcador, usar el valor del input si existe
                coordenadas = st.session_state.get('coordenadas_input', '')
                st.markdown("**Ubicación seleccionada:** Ninguna")
            
            # Mostrar las coordenadas actuales
            if st.session_state.get('marker_position'):
                st.success(f"✅ Coordenadas seleccionadas: {st.session_state['marker_position'][0]:.6f}, {st.session_state['marker_position'][1]:.6f}")
            elif coordenadas_input:
                coords = parse_coordenadas(coordenadas_input)
                if coords:
                    st.session_state['marker_position'] = coords
                    st.session_state['map_center'] = coords
                    st.rerun()
                else:
                    st.error("❌ Formato de coordenadas inválido. Use: latitud, longitud")
        
        # Sección 6: Observaciones
        with st.expander("📝 Observaciones Adicionales", expanded=False):
            observaciones = st.text_area("Ingrese cualquier observación adicional", height=100)
        
        # Botón de envío y validación
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "💾 Guardar Propiedad", 
                use_container_width=True,
                type="primary"
            )
        
        st.markdown("<div style='margin: 10px 0;'><small>* Campos obligatorios</small></div>", unsafe_allow_html=True)
        
        # Validación antes de enviar el formulario
        campos_requeridos = {
            'RUT': (rut, validar_rut(rut) if rut else False, "texto"),
            'Propietario': (propietario, bool(propietario and propietario.strip()), "texto"),
            'N° de contacto': (num_contacto, bool(num_contacto and num_contacto.strip()), "texto"),
            'Dirección': (direccion, bool(direccion and direccion.strip()), "texto"),
            'ROL Propiedad': (rol, bool(rol and rol.strip()), "texto"),
            'Avalúo Total': (avaluo, avaluo > 0, "numero"),
            'M² Terreno': (m2_terreno, m2_terreno > 0, "numero"),
            'M² Construidos': (m2_construidos, m2_construidos > 0, "numero"),
            'Fiscalización DOM': (fiscalizada, bool(fiscalizada), "booleano"),
            'PATENTE COMERCIAL': (patente_comercial, bool(patente_comercial), "texto")
        }
        
        # Verificar si hay campos obligatorios vacíos
        campos_incompletos = [campo for campo, (valor, valido, tipo) in campos_requeridos.items() if not valido]
        
        if submitted:
            # Validar RUT
            if not validar_rut(rut) if rut else True:
                st.error("❌ RUT inválido. Por favor verifique el formato y el dígito verificador.")
                st.stop()  # Detener la ejecución si el RUT no es válido
                
            # Validar campos obligatorios
            if campos_incompletos:
                mensaje_error = "❌ Por favor complete los siguientes campos obligatorios:\n"
                for campo in campos_incompletos:
                    valor_campo, valido, tipo = campos_requeridos[campo]
                    if tipo == "texto" and (not valor_campo or not str(valor_campo).strip()):
                        mensaje_error += f"- {campo}: Campo de texto requerido\n"
                    elif tipo == "numero" and (valor_campo is None or valor_campo <= 0):
                        mensaje_error += f"- {campo}: Debe ser un número mayor a cero\n"
                    elif tipo == "booleano" and not valor_campo:
                        mensaje_error += f"- {campo}: Debe seleccionar una opción\n"
                
                st.error(mensaje_error)
                st.stop()  # Detener la ejecución si hay campos obligatorios faltantes
                
            # Si llegamos aquí, todos los campos obligatorios están completos
            # Validar coordenadas
            if not coordenadas or not st.session_state.get('marker_position'):
                st.error("❌ Por favor seleccione una ubicación en el mapa o ingrese coordenadas válidas.")
                st.stop()  # Detener la ejecución si no hay coordenadas
                
            # Si todo está correcto, continuar con el guardado
            # Asegurarse de que las coordenadas estén en el formato correcto
            if isinstance(st.session_state.get('marker_position'), list) and len(st.session_state['marker_position']) == 2:
                coordenadas = f"{st.session_state['marker_position'][0]}, {st.session_state['marker_position'][1]}"
            
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
                    # Limpiar el formulario después de un envío exitoso
                    st.session_state.opcion_seleccionada = "🏠 Inicio"
                    st.rerun()
                else:
                    st.error("Error al guardar los datos. Por favor, intente nuevamente.")

elif opcion == "Ver/Editar Propiedades":
    st.markdown("""
        <div class='card' style='margin-bottom: 2rem;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 2rem; margin-right: 0.75rem;'>📋</span>
                <div>
                    <h2 style='margin: 0;'>Lista de Propiedades</h2>
                    <p class='subheader' style='margin: 0.25rem 0 0 0;'>Visualice y edite las propiedades registradas</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Crear pestañas para tabla, mapa y estadísticas
    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Datos", "🗺️ Mapa de Propiedades", "📈 Estadísticas"])
    
    propiedades = obtener_propiedades()
    
    if len(propiedades['datos']) > 0:
        with tab1:
            # Convertir a DataFrame
            df = pd.DataFrame(propiedades['datos'])
            
            # Crear filtros para cada columna
            st.sidebar.markdown("### 🔍 Filtros por Columna")
            
            # Diccionario para almacenar los filtros
            filtros = {}
            
            # Mapeo de nombres de columnas amigables a nombres reales en la base de datos
            mapeo_columnas = {
                'RUT': 'rut',
                'Propietario': 'propietario',
                'ROL Propiedad': 'rol_propiedad',
                'Dirección': 'dirección'
            }
            
            # Columnas específicas para filtrar (nombres amigables)
            columnas_filtrables = ['RUT', 'Propietario', 'ROL Propiedad', 'Dirección']
            
            # Crear un filtro para cada columna específica
            for col_amigable in columnas_filtrables:
                if mapeo_columnas[col_amigable] in df.columns:
                    col_real = mapeo_columnas[col_amigable]
                    try:
                        # Convertir a string y limpiar los valores
                        df[col_real] = df[col_real].astype(str).str.strip()
                        
                        # Obtener valores únicos, ordenados y sin valores vacíos
                        valores_unicos = sorted([v for v in df[col_real].dropna().unique().tolist() if v and v != 'nan'])
                        
                        if valores_unicos:  # Solo crear el filtro si hay valores
                            seleccion = st.sidebar.multiselect(
                                f"Filtrar por {col_amigable}",
                                options=valores_unicos,
                                default=[],
                                key=f"filtro_{col_real}",
                                help=f"Busque y seleccione {col_amigable.lower()} para filtrar"
                            )
                            if seleccion:  # Si hay alguna selección, aplicar el filtro
                                filtros[col_real] = seleccion
                    except Exception as e:
                        # Si hay un error al procesar la columna, la omitimos
                        st.sidebar.error(f"Error al crear filtro para {col_amigable}: {str(e)}")
                        continue
            
            # Aplicar filtros al DataFrame
            if filtros:
                for col, valores in filtros.items():
                    if 'Todos' not in valores:  # Si no se seleccionó 'Todos', aplicar el filtro
                        df = df[df[col].astype(str).isin(valores)]
                # Mostrar el DataFrame con los filtros aplicados
                if not df.empty:
                    st.write(f"Mostrando {len(df)} de {len(propiedades['datos'])} propiedades")
                    
                    # Crear una copia del DataFrame para no modificar el original
                    display_df = df.copy()
                    
                    # Configurar las columnas a mostrar
                    column_config = {}
                    
                    # Configurar la columna de miniatura
                    if 'Miniatura' in display_df.columns:
                        # Mover la columna Miniatura al principio
                        cols = ['Miniatura'] + [col for col in display_df.columns if col != 'Miniatura' and col != 'Fotos']
                        display_df = display_df[cols]
                        
                        # Configurar la columna de miniaturas
                        column_config["Miniatura"] = st.column_config.ImageColumn(
                            "Foto",
                            help="Miniatura de la propiedad",
                            width="small"
                        )
                    
                    # Configurar la columna de Fotos (lista completa)
                    if 'Fotos' in display_df.columns:
                        column_config["Fotos"] = st.column_config.ListColumn(
                            "Todas las Fotos",
                            help="Todas las fotos de la propiedad"
                        )
                    
                    # Agregar columna de acciones
                    if 'Acciones' not in display_df.columns:
                        display_df['Acciones'] = ''
                    
                    # Configurar la columna de acciones
                    column_config["Acciones"] = st.column_config.Column(
                        "Acciones",
                        help="Acciones disponibles para la propiedad",
                        width="small"
                    )
                    
                    # Mostrar el editor de datos
                    st.markdown("""
                        <style>
                            img {
                                max-height: 50px;
                                width: auto;
                                border-radius: 4px;
                            }
                            .stDataFrame img {
                                max-height: 50px !important;
                                width: auto !important;
                            }
                            .stButton button {
                                padding: 0.25rem 0.5rem;
                                font-size: 0.8rem;
                            }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Función para manejar la eliminación de propiedades
                    def eliminar_propiedad(propiedad_id, propiedad_info):
                        # Usar el estado de la sesión para controlar la confirmación
                        if f'confirmar_eliminar_{propiedad_id}' not in st.session_state:
                            st.session_state[f'confirmar_eliminar_{propiedad_id}'] = False
                        
                        # Mostrar diálogo de confirmación
                        if not st.session_state[f'confirmar_eliminar_{propiedad_id}']:
                            if st.button(f"🗑️ Eliminar {propiedad_id}", key=f"btn_eliminar_{propiedad_id}", type="primary"):
                                st.session_state[f'confirmar_eliminar_{propiedad_id}'] = True
                                st.rerun()
                        else:
                            st.warning(
                                """
                                ⚠️ **¿Está seguro que desea eliminar esta propiedad?**  
                                
                                **Propietario:** {}  
                                **Dirección:** {}  
                                **RUT:** {}  
                                
                                Esta acción es irreversible y eliminará todos los datos asociados, incluidas las fotos.
                                """.format(
                                    propiedad_info.get('Propietario', 'Sin especificar'),
                                    propiedad_info.get('Dirección', 'Sin especificar'),
                                    propiedad_info.get('RUT', 'Sin especificar')
                                )
                            )
                            
                            # Botones de confirmación
                            col1, col2, _ = st.columns([1, 1, 3])
                            with col1:
                                if st.button("✅ Confirmar eliminación", key=f"confirmar_si_{propiedad_id}", type="primary"):
                                    conn = None
                                    try:
                                        conn = get_db_connection()
                                        cursor = conn.cursor()
                                        
                                        # Obtener información de las fotos para eliminarlas del sistema de archivos
                                        cursor.execute('SELECT ruta_archivo FROM fotos WHERE propiedad_id = ?', (propiedad_id,))
                                        fotos = cursor.fetchall()
                                        
                                        # Eliminar archivos físicos
                                        for foto in fotos:
                                            try:
                                                if foto[0] and os.path.exists(foto[0]):
                                                    os.remove(foto[0])
                                            except Exception as e:
                                                st.error(f"Error al eliminar el archivo {foto[0] if foto[0] else 'desconocido'}: {e}")
                                        
                                        # Eliminar registros de la base de datos
                                        cursor.execute('DELETE FROM fotos WHERE propiedad_id = ?', (propiedad_id,))
                                        cursor.execute('DELETE FROM propiedades WHERE id = ?', (propiedad_id,))
                                        conn.commit()
                                        
                                        st.success("✅ Propiedad eliminada correctamente.")
                                        # Limpiar el estado de confirmación
                                        st.session_state[f'confirmar_eliminar_{propiedad_id}'] = False
                                        # Esperar 1 segundo antes de recargar para que se vea el mensaje
                                        time.sleep(1)
                                        st.rerun()
                                        
                                    except Error as e:
                                        st.error(f"❌ Error al eliminar la propiedad: {str(e)}")
                                        if conn:
                                            conn.rollback()
                                    finally:
                                        if conn:
                                            conn.close()
                            
                            with col2:
                                if st.button("❌ Cancelar", key=f"confirmar_no_{propiedad_id}"):
                                    st.session_state[f'confirmar_eliminar_{propiedad_id}'] = False
                                    st.rerun()
                    
                    # Mostrar botones de acción para cada propiedad
                    for idx, row in display_df.iterrows():
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"✏️ Editar {row['id']}", key=f"editar_{row['id']}"):
                                st.session_state['propiedad_editar'] = row.to_dict()
                                st.session_state['opcion_seleccionada'] = "Agregar Propiedad"
                                st.rerun()
                        with col2:
                            # Llamar a la función de eliminación
                            eliminar_propiedad(row['id'], row)
                    
                    # Mostrar el dataframe sin la columna de acciones
                    display_df = display_df.drop(columns=['Acciones'])
                    
                    # Mostrar el editor de datos
                    edited_df = st.data_editor(
                        display_df,
                        column_config=column_config,
                        num_rows="fixed",
                        use_container_width=True,
                        hide_index=True,
                        key="editor_propiedades"
                    )
                    
                    # Guardar cambios si hay modificaciones
                    if not edited_df.equals(display_df):
                        # Actualizar propiedades en la base de datos
                        for i, propiedad in edited_df.iterrows():
                            guardar_propiedad(propiedad.to_dict())
                        st.success("¡Cambios guardados exitosamente!")
                        st.rerun()
            else:
                st.warning("No hay propiedades que coincidan con los filtros seleccionados.")
        
        # Mostrar estadísticas de filtrado
        if filtros:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📊 Estadísticas de Filtrado")
            st.sidebar.write(f"Propiedades mostradas: **{len(df)}** de {len(propiedades['datos'])}")
            if st.sidebar.button("Limpiar Filtros"):
                for col in columnas_filtrables:
                    if f"filtro_{col}" in st.session_state:
                        st.session_state[f"filtro_{col}"] = []
                st.rerun()
        
        with tab2:
            m = crear_mapa()
            
            # Agregar agrupador de marcadores
            marker_cluster = folium.plugins.MarkerCluster(
                name='Propiedades',
                overlay=True,
                control=True,
                icon_create_function=None
            ).add_to(m)
            
            # Agregar marcadores para cada propiedad con coordenadas válidas
            for propiedad in propiedades['datos']:
                # Verificar si la propiedad tiene coordenadas y son válidas
                coordenadas = propiedad.get('Coordenadas') or propiedad.get('coordenadas')
                if coordenadas and isinstance(coordenadas, str):
                    coords = parse_coordenadas(coordenadas)
                    if coords:
                        # Crear contenido HTML para el popup
                        popup_html = f"""
                        <div style="width: 250px;">
                            <h4 style="margin: 5px 0; color: #1e3d59;">📌 {propiedad.get('Dirección', 'Sin dirección')}</h4>
                            <hr style="margin: 5px 0; border: 0.5px solid #ddd;">
                            <p style="margin: 3px 0; font-size: 13px;">
                                <strong>ROL:</strong> {propiedad.get('ROL Propiedad', 'N/A')}<br>
                                <strong>Propietario:</strong> {propiedad.get('Propietario', 'N/A')}<br>
                                <strong>RUT:</strong> {propiedad.get('RUT', 'N/A')}<br>
                                <strong>M² Terreno:</strong> {propiedad.get('M² Terreno', 'N/A')}<br>
                                <strong>M² Construidos:</strong> {propiedad.get('M² Construidos', 'N/A')}<br>
                                <strong>Fiscalización DOM:</strong> {propiedad.get('Fiscalización DOM', 'N/A')}
                            </p>
                        """
                        
                        # Crear iframe para el popup
                        iframe = folium.IFrame(html=popup_html, width=280, height=180)
                        popup = folium.Popup(iframe, max_width=300)
                        
                        # Crear marcador con popup personalizado
                        folium.Marker(
                            location=coords,
                            popup=popup,
                            icon=folium.Icon(
                                color='blue',
                                icon='home' if propiedad.get('Destino DOM') == 'Habitacional' else 'info-sign',
                                prefix='fa'
                            ),
                            tooltip=f"Ver detalles de {propiedad.get('Dirección', 'la propiedad')}"
                        ).add_to(marker_cluster)
            
            # Añadir control de capas
            folium.LayerControl().add_to(m)
            
            # Añadir control de pantalla completa
            folium.plugins.Fullscreen(
                position="topright",
                title="Pantalla completa",
                title_cancel="Salir de pantalla completa",
                force_separate_button=True
            ).add_to(m)
            
            # Mostrar el mapa
            folium_static(m, width=1200, height=700)
        
        with tab3:
            st.markdown("""<h3 style='color: #1e3d59;'>📈 Estado de Fiscalización de las Propiedades</h3>""", unsafe_allow_html=True)
            
            # Mostrar estadísticas detalladas
            st.subheader("Análisis por Fiscalización DOM")
            fiscalizadas_count = {}
            for propiedad in propiedades['datos']:
                # Usar get() con valor por defecto 'No Especificada' si la clave no existe
                fiscalizacion_dom = propiedad.get('Fiscalización DOM', 'No Especificada')
                # Si el valor es None o vacío, usar 'No Especificada'
                if not fiscalizacion_dom:
                    fiscalizacion_dom = 'No Especificada'
                if fiscalizacion_dom in fiscalizadas_count:
                    fiscalizadas_count[fiscalizacion_dom] += 1
                else:
                    fiscalizadas_count[fiscalizacion_dom] = 1
            
            # Gráfico de torta para Fiscalización DOM
            labels = list(fiscalizadas_count.keys())
            values = list(fiscalizadas_count.values())
            total = sum(values)
            
            # Crear etiquetas personalizadas con valor y porcentaje
            custom_labels = [f"{label}<br>({value} - {value/total*100:.1f}%)" 
                          for label, value in zip(labels, values)]
            
            fig1 = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.3,
                textinfo='none',  # Ocultar etiquetas predeterminadas
                marker=dict(colors=['#2ecc71', '#e74c3c', '#3498db', '#f39c12', '#9b59b6']),
                hoverinfo='label+percent+value',
                texttemplate='%{percent:.1%}',
                textposition='inside',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{label}</b><br>' +
                              'Cantidad: %{value}<br>' +
                              'Porcentaje: %{percent:.1%}<extra></extra>'
            )])
            
            # Actualizar diseño del gráfico
            fig1.update_layout(
                title=dict(
                    text='Distribución por Estado de Fiscalización',
                    font=dict(size=18, color='#1e3d59'),
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12)
                ),
                margin=dict(t=60, b=20, l=20, r=20),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=14,
                    font_family="Arial"
                )
            )
            
            # Agregar anotaciones con los valores
            fig1.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=14,
                insidetextorientation='radial',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
            # Mostrar el gráfico
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            
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
    st.markdown("""
        <div class='card' style='margin-bottom: 2rem;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 2rem; margin-right: 0.75rem;'>🔍</span>
                <div>
                    <h2 style='margin: 0;'>Buscar Propiedades</h2>
                    <p class='subheader' style='margin: 0.25rem 0 0 0;'>Busque propiedades por RUT, Propietario, Dirección o ROL Propiedad</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
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
        # Crear DataFrame con los datos
        df = pd.DataFrame(propiedades['datos'])
        
        # Exportar a Excel usando BytesIO
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Propiedades')
        excel_data = excel_buffer.getvalue()
        
        # Botón de descarga para Excel
        st.download_button(
            label="📊 Descargar como Excel",
            data=excel_data,
            file_name="catastro_propiedades.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Mostrar botón para exportar a CSV
        if not df.empty:
            # Asegurarse de que la columna 'Fotos' existe antes de intentar eliminarla
            csv_columns = [col for col in df.columns if col != 'Fotos']
            csv = df[csv_columns].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Exportar resultados a CSV",
                data=csv,
                file_name='busqueda_propiedades.csv',
                mime='text/csv',
            )
    else:
        st.info("No hay datos para exportar.")

elif opcion == "Gestionar Fotos":
    st.markdown("""
        <div class='card' style='margin-bottom: 2rem;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 2rem; margin-right: 0.75rem;'>🖼️</span>
                <div>
                    <h2 style='margin: 0;'>Gestión de Fotos de Propiedades</h2>
                    <p class='subheader' style='margin: 0.25rem 0 0 0;'>Agregue o visualice fotos de las propiedades</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Seleccionar propiedad
    propiedades = obtener_propiedades()
    
    if 'datos' in propiedades and propiedades['datos']:
        # Crear lista de propiedades para el selector de manera segura
        propiedades_lista = []
        for i, propiedad in enumerate(propiedades['datos']):
            # Usar get() con valores por defecto para manejar claves faltantes
            rut = propiedad.get('RUT', 'Sin RUT')
            propietario = propiedad.get('Propietario', 'Sin propietario')
            direccion = propiedad.get('Dirección', 'Sin dirección')
            
            # Crear un identificador único para cada propiedad
            id_unico = f"{i:04d}"  # Usamos el índice como identificador único
            
            # Agregar a la lista con el identificador único
            propiedades_lista.append({
                'id': id_unico,
                'texto': f"{rut} - {propietario} - {direccion}",
                'propiedad': propiedad
            })
        
        # Mostrar el selector con los textos formateados
        opcion_seleccionada = st.selectbox(
            "Seleccione una propiedad:",
            [p['texto'] for p in propiedades_lista],
            index=0
        )
        
        # Obtener la propiedad seleccionada
        propiedad_seleccionada = next((p for p in propiedades_lista if p['texto'] == opcion_seleccionada), None)
        
        # Obtener la propiedad seleccionada
        if propiedad_seleccionada is not None:
            propiedad = propiedad_seleccionada['propiedad']
        else:
            st.error("No se pudo cargar la propiedad seleccionada.")
            st.stop()
        
        st.markdown("### Información de la Propiedad")
        col1, col2 = st.columns(2)
        with col1:
            # Usar get() con valores por defecto para manejar claves faltantes
            st.write(f"**Propietario:** {propiedad.get('Propietario', 'No especificado')}")
            st.write(f"**RUT:** {propiedad.get('RUT', 'No especificado')}")
        with col2:
            st.write(f"**Dirección:** {propiedad.get('Dirección', 'No especificada')}")
            st.write(f"**ROL Propiedad:** {propiedad.get('ROL Propiedad', 'No especificado')}")
        
        st.markdown("---")
        st.markdown("### Fotos de la Propiedad")
        
        # Agregar estilos CSS para el modal
        st.markdown("""
        <style>
            /* Estilo del modal */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
                overflow: auto;
            }
            
            /* Contenido del modal */
            .modal-content {
                margin: auto;
                display: block;
                max-width: 90%;
                max-height: 90%;
                margin-top: 2%;
            }
            
            /* Botón de cierre */
            .close {
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }
            
            /* Miniaturas de fotos */
            .thumbnail {
                cursor: pointer;
                transition: 0.3s;
                border-radius: 5px;
                margin-bottom: 10px;
                max-height: 200px;
                object-fit: cover;
            }
            
            .thumbnail:hover {
                opacity: 0.7;
            }
            
            /* Contenedor de miniaturas */
            .gallery {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                padding: 10px;
            }
            
            .gallery-item {
                position: relative;
            }
            
            .delete-btn {
                position: absolute;
                top: 5px;
                right: 5px;
                background: rgba(255, 0, 0, 0.7);
                color: white;
                border: none;
                border-radius: 50%;
                width: 25px;
                height: 25px;
                font-size: 14px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .delete-btn:hover {
                background: rgba(255, 0, 0, 1);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # HTML para el modal
        st.markdown("""
        <div id="imageModal" class="modal">
            <span class="close">&times;</span>
            <img class="modal-content" id="modalImage">
        </div>
        """, unsafe_allow_html=True)
        
        # JavaScript para el modal
        st.markdown("""
        <script>
            // Obtener el modal
            var modal = document.getElementById('imageModal');
            var modalImg = document.getElementById("modalImage");
            var span = document.getElementsByClassName("close")[0];
            
            // Función para abrir el modal con la imagen seleccionada
            function openModal(imgSrc) {
                modal.style.display = "block";
                modalImg.src = imgSrc;
                document.body.style.overflow = 'hidden'; // Deshabilitar scroll
            }
            
            // Cerrar el modal al hacer clic en la X
            span.onclick = function() {
                modal.style.display = "none";
                document.body.style.overflow = 'auto'; // Habilitar scroll
            }
            
            // Cerrar el modal al hacer clic fuera de la imagen
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                    document.body.style.overflow = 'auto'; // Habilitar scroll
                }
            }
            
            // Cerrar con la tecla ESC
            document.onkeydown = function(evt) {
                evt = evt || window.event;
                if (evt.key === 'Escape') {
                    modal.style.display = "none";
                    document.body.style.overflow = 'auto'; // Habilitar scroll
                }
            };
        </script>
        """, unsafe_allow_html=True)
        
        # Mostrar fotos existentes
        fotos = propiedad['Fotos'] if isinstance(propiedad['Fotos'], list) else []
        
        if fotos:
            st.markdown("### Fotos existentes")
            st.markdown("<div class='gallery'>", unsafe_allow_html=True)
            
            for i, foto in enumerate(fotos):
                # Mostrar miniatura
                # Crear un botón de eliminación con Streamlit
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style='position: relative;'>
                            <img src='{foto}' class='thumbnail' 
                                 onclick='openModal("{foto}")' 
                                 style='width: 100%; height: 200px; object-fit: cover; border-radius: 5px; cursor: pointer;' />
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("×", key=f"del_photo_{i}", 
                                   help="Eliminar esta foto",
                                   use_container_width=True,
                                   type="secondary"):
                            try:
                                # Eliminar el archivo de la foto
                                if os.path.exists(foto):
                                    os.remove(foto)
                                
                                # Actualizar la lista de fotos en la base de datos
                                fotos_actualizadas = [f for j, f in enumerate(fotos) if j != i]
                                guardar_fotos(propiedad['id'], fotos_actualizadas)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error al eliminar la foto: {e}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay fotos para esta propiedad.")
        
        # Subir nuevas fotos
        st.markdown("### Agregar Nuevas Fotos")
        uploaded_files = st.file_uploader(
            "Seleccione una o más fotos para esta propiedad (Máx. 10MB por archivo)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Puede seleccionar múltiples fotos a la vez"
        )
        
        if uploaded_files:
            # Mostrar resumen de archivos seleccionados
            st.info(f"📷 {len(uploaded_files)} foto(s) seleccionada(s). Tamaño total: {sum(f.size for f in uploaded_files) / (1024*1024):.1f} MB")
            
            if st.button("📤 Subir Fotos", type="primary", use_container_width=True):
                nuevas_fotos = []
                total_files = len(uploaded_files)
                
                # Crear barras de progreso
                progress_bar = st.progress(0, text="Preparando para subir...")
                status_text = st.empty()
                
                # Crear contenedor para miniaturas de vista previa
                preview_container = st.container()
                
                for i, uploaded_file in enumerate(uploaded_files, 1):
                    try:
                        # Actualizar progreso
                        progress_percent = int((i / total_files) * 100)
                        status_text.text(f"Procesando {i} de {total_files}: {uploaded_file.name[:30]}...")
                        progress_bar.progress(progress_percent, text=f"Procesando {i} de {total_files} fotos...")
                        
                        # Mostrar vista previa de la imagen que se está subiendo
                        with preview_container:
                            with st.expander(f"Vista previa: {uploaded_file.name}", expanded=False):
                                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
                        
                        # Validar tamaño del archivo (máx 10MB)
                        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                            st.warning(f"La foto {uploaded_file.name} supera el tamaño máximo de 10MB y no se subirá.")
                            continue
                        
                        # Crear directorio de uploads si no existe
                        os.makedirs('uploads', exist_ok=True)
                        
                        # Generar nombre de archivo único
                        timestamp = int(time.time())
                        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                        file_name = f"{propiedad['RUT']}_{timestamp}_{i}{file_extension}"
                        file_path = os.path.join('uploads', file_name)
                        
                        # Mostrar indicador de progreso para esta foto
                        with st.spinner(f"Subiendo {uploaded_file.name}..."):
                            # Simular progreso para archivos pequeños
                            for _ in range(3):
                                time.sleep(0.1)
                                progress_bar.progress(progress_percent + 5, text=f"Subiendo {i} de {total_files}...")
                            
                            # Guardar el archivo
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Agregar a la lista de nuevas fotos
                            nuevas_fotos.append(file_path)
                        
                        # Mostrar éxito para esta foto
                        st.success(f"✓ {uploaded_file.name} subida correctamente")
                        
                    except Exception as e:
                        st.error(f"❌ Error al procesar {uploaded_file.name}: {str(e)}")
                
                # Procesar las fotos subidas
                if nuevas_fotos:
                    with st.spinner("Guardando en la base de datos..."):
                        # Obtener fotos existentes
                        fotos_existentes = propiedad.get('Fotos', [])
                        if not isinstance(fotos_existentes, list):
                            fotos_existentes = []
                        
                        # Combinar fotos existentes con nuevas
                        todas_las_fotos = fotos_existentes + nuevas_fotos
                        
                        # Actualizar barra de progreso
                        progress_bar.progress(95, text="Guardando en la base de datos...")
                        
                        # Guardar en la base de datos
                        if guardar_fotos(propiedad['id'], todas_las_fotos):
                            progress_bar.progress(100, text="¡Completado!")
                            status_text.success(f"✅ ¡{len(nuevas_fotos)} de {total_files} fotos guardadas correctamente!")
                            
                            # Esperar un momento antes de recargar
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            status_text.error("❌ Error al guardar las fotos en la base de datos.")
                else:
                    status_text.warning("⚠️ No se pudo guardar ninguna foto.")
                    progress_bar.empty()
                
                # Limpiar archivos subidos
                st.session_state.file_uploader_key = str(time.time())
    else:
        st.info("No hay propiedades registradas para gestionar fotos.")

elif opcion == "Exportar Datos":
    st.markdown("""
        <div class='card' style='margin-bottom: 2rem;'>
            <div style='display: flex; align-items: center;'>
                <span style='font-size: 2rem; margin-right: 0.75rem;'>📊</span>
                <div>
                    <h2 style='margin: 0;'>Exportar Datos</h2>
                    <p class='subheader' style='margin: 0.25rem 0 0 0;'>Exporte los datos de las propiedades a diferentes formatos</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener todas las propiedades
    propiedades = obtener_propiedades(por_pagina=1000)  # Número grande para obtener todas las propiedades
    
    if 'datos' in propiedades and propiedades['datos']:
        # Convertir a DataFrame para facilitar la exportación
        df = pd.DataFrame(propiedades['datos'])
        
        # Mostrar vista previa de los datos
        st.subheader("Vista previa de los datos a exportar")
        st.dataframe(df.head())
        
        # Opciones de exportación
        st.subheader("Opciones de exportación")
        
        # Exportar a Excel
        if st.button("💾 Exportar a Excel", use_container_width=True):
            try:
                # Crear un archivo Excel en memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Propiedades')
                
                # Crear un botón de descarga
                st.download_button(
                    label="⬇️ Descargar archivo Excel",
                    data=output.getvalue(),
                    file_name='propiedades_exportadas.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al exportar a Excel: {str(e)}")
        
        # Exportar a CSV
        if st.button("📄 Exportar a CSV", use_container_width=True):
            try:
                # Crear un archivo CSV en memoria
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                
                # Crear un botón de descarga
                st.download_button(
                    label="⬇️ Descargar archivo CSV",
                    data=csv,
                    file_name='propiedades_exportadas.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al exportar a CSV: {str(e)}")
        
        # Exportar a JSON
        if st.button("🔤 Exportar a JSON", use_container_width=True):
            try:
                # Convertir a JSON
                json_data = df.to_json(orient='records', force_ascii=False, indent=4)
                
                # Crear un botón de descarga
                st.download_button(
                    label="⬇️ Descargar archivo JSON",
                    data=json_data,
                    file_name='propiedades_exportadas.json',
                    mime='application/json',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al exportar a JSON: {str(e)}")
    else:
        st.info("No hay propiedades registradas para exportar.")


