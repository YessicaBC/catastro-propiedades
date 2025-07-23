# Estilos CSS personalizados para el menú
st.markdown("""
<style>
    /* Estilo general del menú */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3d59 0%, #1a365d 100%);
        color: white;
    }
    
    /* Estilo para los botones del menú */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 5px 0;
        text-align: left;
        transition: all 0.3s ease;
        background-color: transparent;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 15px;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.1);
        transform: translateX(5px);
        border-left: 3px solid #ff6b6b;
    }
    
    /* Estilo para el botón activo */
    .stButton>button:active,
    .stButton>button:focus {
        background-color: rgba(255, 255, 255, 0.2);
        border-left: 3px solid #ff6b6b;
        box-shadow: none;
    }
    
    /* Estilo para el logo */
    .logo-container {
        text-align: center;
        padding: 15px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Estilo para el título del menú */
    .menu-title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        margin: 15px 0 20px 0;
        padding: 0 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Estilo para los iconos */
    .menu-icon {
        margin-right: 10px;
        font-size: 18px;
    }
    
    /* Separador de secciones */
    .menu-separator {
        height: 1px;
        background-color: rgba(255, 255, 255, 0.1);
        margin: 15px 0;
    }
    
    /* Versión de la aplicación */
    .app-version {
        position: absolute;
        bottom: 10px;
        left: 0;
        right: 0;
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        font-size: 12px;
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
        {"icon": "🏠", "label": "Inicio", "key": "Inicio"},
        {"icon": "📋", "label": "Gestión de Propiedades", "key": "Gestión de Propiedades"},
        {"icon": "✏️", "label": "Ver/Editar Propiedades", "key": "Ver/Editar Propiedades"},
        {"icon": "🔍", "label": "Buscar Propiedades", "key": "Buscar Propiedades"},
        {"icon": "📊", "label": "Reportes", "key": "Reportes"},
        {"icon": "📤", "label": "Exportar Datos", "key": "Exportar Datos"},
        {"icon": "🖼️", "label": "Gestionar Fotos", "key": "Gestionar Fotos"}
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
        if st.button(
            f"{item['icon']} {item['label']}",
            key=f"menu_{item['key']}",
            use_container_width=True,
            help=f"Ir a {item['label']}"
        ):
            st.session_state.menu_seleccionado = item["key"]
            st.experimental_rerun()
        
        # Aplicar estilo al botón activo
        st.markdown(
            f"""
            <style>
                div[data-testid="stButton"]:has(button:contains('{item["label"]}')) > button {{
                    {button_style}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
    
    # Separador antes de las opciones de sistema
    st.markdown('<div class="menu-separator"></div>', unsafe_allow_html=True)
    
    # Opciones de sistema
    system_items = [
        {"icon": "⚙️", "label": "Configuración", "key": "Configuración"},
        {"icon": "❓", "label": "Ayuda", "key": "Ayuda"}
    ]
    
    for item in system_items:
        if st.button(
            f"{item['icon']} {item['label']}",
            key=f"menu_{item['key']}",
            use_container_width=True,
            help=f"{item['label']} del sistema"
        ):
            st.session_state.menu_seleccionado = item["key"]
            st.experimental_rerun()
    
    # Versión de la aplicación
    st.markdown('''
    <div class="app-version">
        v1.0.0<br>
        <small>© 2025 Municipalidad de Independencia</small>
    </div>
    ''', unsafe_allow_html=True)
