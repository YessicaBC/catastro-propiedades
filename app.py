import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
import time

# Configuración de la página
st.set_page_config(
    page_title="Catastro Comunal de Independencia",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from datetime import datetime
import time

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

# Crear directorio para almacenar imágenes si no existe
import os
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Inicializar el DataFrame en la sesión si no existe
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        'RUT', 'Propietario', 'Dirección', 'ROL', 'Avalúo Total',
        'Destino SII', 'Destino según Terreno', 'Destino DOM',
        'N° en Terreno', 'Coordenadas', 'Fiscalizada DOM', 'M2 Terreno',
        'M2 Construidos', 'Línea de Construcción',
        'Año de Construcción', 'Expediente DOM', 'Observaciones',
        'Fotos'  # Lista de rutas de fotos
    ])
    # Inicializar la columna de fotos como lista vacía para todas las filas
    st.session_state.df['Fotos'] = st.session_state.df['Fotos'].apply(lambda x: [] if pd.isna(x) else x)

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

# Función para validar RUT chileno
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
    st.markdown("""<h2>📝 Agregar Nueva Propiedad</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Complete el formulario con los datos de la propiedad</p>""", unsafe_allow_html=True)
    
    with st.form("formulario_propiedad"):
        col1, col2 = st.columns(2)
        
        with col1:
            rut = st.text_input("RUT (formato: 12345678-9)")
            propietario = st.text_input("Propietario")
            direccion = st.text_input("Dirección")
            rol = st.text_input("ROL")
            avaluo = st.number_input("Avalúo Total", min_value=0)
            destino_sii = st.text_input("Destino SII")
            destino_terreno = st.text_input("Destino según Terreno")
            destino_dom = st.text_input("Destino DOM")
            
        with col2:
            num_terreno = st.text_input("N° en Terreno")
            coordenadas = st.text_input("Coordenadas (Lat, Long)", help="Ingrese las coordenadas en formato: latitud, longitud (ejemplo: -33.4172, -70.6506)")
            if coordenadas:
                coords = parse_coordenadas(coordenadas)
                if coords:
                    st.success("Coordenadas válidas")
                    with st.expander("Ver ubicación en mapa"):
                        m = crear_mapa(coords)
                        folium.Marker(
                            coords,
                            popup="Nueva propiedad",
                            icon=folium.Icon(color='red', icon='info-sign')
                        ).add_to(m)
                        folium_static(m)
                else:
                    st.error("Formato de coordenadas inválido. Use: latitud, longitud")
            fiscalizada = st.selectbox(
                "Fiscalizada DOM",
                options=["CERRADA", "SIN PATENTE AL DIA", "CON PATENTE AL DIA", "VIVIENDA COLECTIVA", "SIN INFORMACION"],
                index=None,
                placeholder="Seleccione una opción")
            m2_terreno = st.number_input("M2 Terreno", min_value=0.0)
            m2_construidos = st.number_input("M2 Construidos", min_value=0.0)
            linea_construccion = st.text_input("Línea de Construcción")
            año_construccion = st.number_input("Año de Construcción", 
                                             min_value=1800, 
                                             max_value=datetime.now().year)
            expediente = st.text_input("Expediente DOM")
            
        observaciones = st.text_area("Observaciones")
        submitted = st.form_submit_button("Guardar Propiedad")
        
        if submitted:
            if not validar_rut(rut):
                st.markdown("""<div class='error-message'>❌ RUT inválido. Por favor verifique el formato y el dígito verificador.</div>""", unsafe_allow_html=True)
            else:
                # Mostrar spinner durante el proceso
                with st.spinner('Guardando información...'):
                    time.sleep(0.5)  # Simular proceso
                    nueva_propiedad = pd.DataFrame([{
                        'RUT': rut,
                        'Propietario': propietario,
                        'Dirección': direccion,
                        'ROL': rol,
                        'Avalúo Total': avaluo,
                        'Destino SII': destino_sii,
                        'Destino según Terreno': destino_terreno,
                        'Destino DOM': destino_dom,
                        'N° en Terreno': num_terreno,
                        'Coordenadas': coordenadas,
                        'Fiscalizada DOM': fiscalizada,
                        'M2 Terreno': m2_terreno,
                        'M2 Construidos': m2_construidos,
                        'Línea de Construcción': linea_construccion,
                        'Año de Construcción': año_construccion,
                        'Expediente DOM': expediente,
                        'Observaciones': observaciones,
                        'Fotos': []  # Inicializar lista vacía para fotos
                    }])
                    st.session_state.df = pd.concat([st.session_state.df, nueva_propiedad], ignore_index=True)
                    st.markdown("""<div class='success-message'>✅ Propiedad agregada exitosamente!</div>""", unsafe_allow_html=True)

elif opcion == "Ver/Editar Propiedades":
    st.markdown("""<h2>📋 Lista de Propiedades</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Visualice y edite las propiedades registradas</p>""", unsafe_allow_html=True)
    
    # Crear pestañas para tabla, mapa y estadísticas
    tab1, tab2, tab3 = st.tabs(["📋 Tabla de Datos", "🗺️ Mapa de Propiedades", "📈 Estadísticas"])
    
    if len(st.session_state.df) > 0:
        with tab1:
            st.data_editor(st.session_state.df, num_rows="dynamic")
        
        with tab2:
            m = crear_mapa()
            # Agregar marcadores para cada propiedad con coordenadas válidas
            for idx, row in st.session_state.df.iterrows():
                if isinstance(row['Coordenadas'], str):
                    coords = parse_coordenadas(row['Coordenadas'])
                    if coords:
                        folium.Marker(
                            coords,
                            popup=f"ROL: {row['ROL']}<br>Dirección: {row['Dirección']}<br>Propietario: {row['Propietario']}",
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(m)
            folium_static(m)
        
        with tab3:
            st.markdown("""<h3 style='color: #1e3d59;'>📈 Distribución de Propiedades Fiscalizadas</h3>""", unsafe_allow_html=True)
            
            # Calcular la distribución de propiedades fiscalizadas
            fiscalizadas_count = st.session_state.df['Fiscalizada DOM'].value_counts()
            
            # Crear gráfico de dona con Plotly
            fig = go.Figure(data=[go.Pie(
                labels=fiscalizadas_count.index,
                values=fiscalizadas_count.values,
                hole=0.4,
                marker_colors=['#FF9800', '#f44336', '#4CAF50', '#2196F3', '#9E9E9E']
            )])
            
            fig.update_layout(
                title='Propiedades Fiscalizadas vs No Fiscalizadas',
                annotations=[dict(text=f'Total: {len(st.session_state.df)}', x=0.5, y=0.5, font_size=20, showarrow=False)],
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            
            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar estadísticas detalladas en dos filas
            col1, col2, col3 = st.columns(3)
            
            # Primera fila
            with col1:
                st.metric(
                    label="CERRADA",
                    value=fiscalizadas_count.get('CERRADA', 0),
                    delta=f"{(fiscalizadas_count.get('CERRADA', 0) / len(st.session_state.df) * 100):.1f}%" if len(st.session_state.df) > 0 else "0%"
                )
            with col2:
                st.metric(
                    label="SIN PATENTE AL DIA",
                    value=fiscalizadas_count.get('SIN PATENTE AL DIA', 0),
                    delta=f"{(fiscalizadas_count.get('SIN PATENTE AL DIA', 0) / len(st.session_state.df) * 100):.1f}%" if len(st.session_state.df) > 0 else "0%"
                )
            with col3:
                st.metric(
                    label="CON PATENTE AL DIA",
                    value=fiscalizadas_count.get('CON PATENTE AL DIA', 0),
                    delta=f"{(fiscalizadas_count.get('CON PATENTE AL DIA', 0) / len(st.session_state.df) * 100):.1f}%" if len(st.session_state.df) > 0 else "0%"
                )
            
            # Segunda fila
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric(
                    label="VIVIENDA COLECTIVA",
                    value=fiscalizadas_count.get('VIVIENDA COLECTIVA', 0),
                    delta=f"{(fiscalizadas_count.get('VIVIENDA COLECTIVA', 0) / len(st.session_state.df) * 100):.1f}%" if len(st.session_state.df) > 0 else "0%"
                )
            with col5:
                st.metric(
                    label="SIN INFORMACION",
                    value=fiscalizadas_count.get('SIN INFORMACION', 0),
                    delta=f"{(fiscalizadas_count.get('SIN INFORMACION', 0) / len(st.session_state.df) * 100):.1f}%" if len(st.session_state.df) > 0 else "0%"
                )
    else:
        st.info("No hay propiedades registradas.")

elif opcion == "Buscar Propiedades":
    st.markdown("""<h2>🔍 Buscar Propiedades</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Busque propiedades por RUT, Propietario, Dirección o ROL</p>""", unsafe_allow_html=True)
    
    busqueda = st.text_input("Ingrese término de búsqueda (RUT, Propietario, Dirección, ROL)")
    
    if busqueda:
        resultado = st.session_state.df[
            st.session_state.df.apply(lambda row: 
                busqueda.lower() in str(row['RUT']).lower() or
                busqueda.lower() in str(row['Propietario']).lower() or
                busqueda.lower() in str(row['Dirección']).lower() or
                busqueda.lower() in str(row['ROL']).lower(),
                axis=1
            )
        ]
        
        if len(resultado) > 0:
            st.write(resultado)
        else:
            st.info("No se encontraron propiedades que coincidan con la búsqueda.")

elif opcion == "Exportar Datos":
    st.markdown("""<h2>📊 Exportar Datos</h2>""", unsafe_allow_html=True)
    st.markdown("""<p style='color: #666; margin-bottom: 2rem;'>Exporte los datos del catastro en formato Excel</p>""", unsafe_allow_html=True)
    
    if len(st.session_state.df) > 0:
        # Exportar a Excel
        excel_file = st.session_state.df.to_excel(index=False)
        st.download_button(
            label="Descargar como Excel",
            data=excel_file,
            file_name="catastro_propiedades.xlsx",
            mime="application/vnd.ms-excel"
        )
        
        df_resultados = st.session_state.df
        st.dataframe(df_resultados)
        
        # Mostrar botón para exportar resultados
        if not df_resultados.empty:
            csv = df_resultados.drop(columns=['Fotos']).to_csv(index=False, encoding='utf-8-sig')
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
    if not st.session_state.df.empty:
        # Crear lista de propiedades para el selector
        propiedades = st.session_state.df.apply(
            lambda x: f"{x['RUT']} - {x['Propietario']} - {x['Dirección']}", 
            axis=1
        ).tolist()
        
        propiedad_seleccionada = st.selectbox(
            "Seleccione una propiedad:",
            propiedades,
            index=0
        )
        
        # Obtener el índice de la propiedad seleccionada
        idx = propiedades.index(propiedad_seleccionada)
        propiedad = st.session_state.df.iloc[idx]
        
        st.markdown("### Información de la Propiedad")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Propietario:** {propiedad['Propietario']}")
            st.write(f"**RUT:** {propiedad['RUT']}")
        with col2:
            st.write(f"**Dirección:** {propiedad['Dirección']}")
            st.write(f"**ROL:** {propiedad['ROL']}")
        
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
                            st.session_state.df.at[idx, 'Fotos'] = fotos
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
                for uploaded_file in uploaded_files:
                    # Guardar el archivo en la carpeta uploads
                    file_path = os.path.join('uploads', f"{propiedad['RUT']}_{int(time.time())}_{uploaded_file.name}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Agregar la ruta a la lista de fotos
                    if not isinstance(propiedad['Fotos'], list):
                        st.session_state.df.at[idx, 'Fotos'] = []
                    st.session_state.df.at[idx, 'Fotos'].append(file_path)
                
                st.success("¡Fotos guardadas correctamente!")
                st.rerun()
    else:
        st.info("No hay propiedades registradas para gestionar fotos.")
