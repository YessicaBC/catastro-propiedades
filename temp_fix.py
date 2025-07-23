# Script para actualizar el menú de navegación

def fix_menu():
    # Ruta del archivo original
    file_path = r'c:\Users\YBUSTAMANTEC\Desktop\catastro-propiedades\app.py'
    
    try:
        # Leer el contenido actual
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar si ya tiene la inicialización de session_state
        if "if 'opcion_seleccionada' not in st.session_state:" not in content:
            # Agregar la inicialización después de las importaciones
            content = content.replace(
                'from sqlite3 import Error\n\n',
                'from sqlite3 import Error\n\n# Inicializar estado de la sesión\nif \'opcion_seleccionada\' not in st.session_state:\n    st.session_state.opcion_seleccionada = "🏠 Inicio"\n\n'
            )
        
        # Reemplazar el menú de radio por botones
        content = content.replace(
            '# Mostrar las opciones como botones de radio\n    opcion_seleccionada = st.radio(\n        "Seleccione una opción",\n        options=[f"{icono} {nombre}" for icono, nombre in opciones],\n        label_visibility="collapsed"\n    )',
            '''# Mostrar las opciones como botones
    for icono, nombre in opciones:
        opcion = f"{icono} {nombre}"
        if st.button(opcion, key=f"menu_{nombre}", use_container_width=True):
            st.session_state.opcion_seleccionada = opcion
    
    # Usar el valor de la sesión
    opcion_seleccionada = st.session_state.opcion_seleccionada'''
        )
        
        # Guardar los cambios
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        return True
    except Exception as e:
        print(f"Error al actualizar el archivo: {e}")
        return False

if __name__ == "__main__":
    if fix_menu():
        print("Menú actualizado exitosamente.")
    else:
        print("No se pudo actualizar el menú.")
