def fix_menu_in_app():
    # Leer el archivo original
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Definir el código del menú corregido
    fixed_menu_code = """    # Opciones del menú con sus respectivos íconos
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
    opcion = next((nombre for icono, nombre in opciones if icono in opcion_seleccionada), opcion_seleccionada)"""
    
    # Reemplazar la sección del menú en el contenido
    import re
    pattern = r'(# Opciones del menú con sus respectivos íconos\n.*?opcion = next\(.*?\))'
    new_content = re.sub(pattern, fixed_menu_code, content, flags=re.DOTALL)
    
    # Guardar los cambios
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Menú corregido exitosamente.")

if __name__ == "__main__":
    fix_menu_in_app()
