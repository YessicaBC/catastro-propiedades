def fix_menu_buttons():
    # Opciones del menú con sus respectivos íconos
    opciones = [
        ("🏠", "Inicio"),
        ("📝", "Agregar Propiedad"),
        ("📋", "Ver/Editar Propiedades"),
        ("🔍", "Buscar Propiedades"),
        ("🖼️", "Gestionar Fotos"),
        ("📊", "Exportar Datos")
    ]
    
    # Mostrar las opciones como botones con claves únicas
    for i, (icono, nombre) in enumerate(opciones):
        opcion = f"{icono} {nombre}"
        if st.button(opcion, key=f"menu_btn_{i}", use_container_width=True):
            st.session_state.opcion_seleccionada = opcion
    
    # Usar el valor de la sesión
    opcion_seleccionada = st.session_state.opcion_seleccionada
    
    # Obtener solo el nombre de la opción seleccionada (sin el ícono)
    opcion = next((nombre for icono, nombre in opciones if icono in opcion_seleccionada), opcion_seleccionada)
    
    return opcion
