# Código para actualizar el menú de navegación

# Reemplazar la sección del menú de navegación con el siguiente código:

    # Mostrar las opciones como botones
    for icono, nombre in opciones:
        opcion = f"{icono} {nombre}"
        if st.button(opcion, key=f"menu_{nombre}", use_container_width=True):
            st.session_state.opcion_seleccionada = opcion
    
    # Usar el valor de la sesión
    opcion_seleccionada = st.session_state.opcion_seleccionada

# Asegúrate de que al inicio del archivo, después de las importaciones, esté:
# Inicializar estado de la sesión
if 'opcion_seleccionada' not in st.session_state:
    st.session_state.opcion_seleccionada = "🏠 Inicio"
