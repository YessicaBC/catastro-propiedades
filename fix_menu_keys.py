# Script para actualizar las claves del menú

def update_menu_keys():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Encontrar la sección del menú
        menu_start = -1
        for i, line in enumerate(lines):
            if '# Mostrar las opciones como botones' in line:
                menu_start = i
                break
        
        if menu_start == -1:
            print("No se encontró la sección del menú.")
            return False
        
        # Actualizar las claves en el bucle del menú
        i = menu_start
        while i < len(lines) and 'opcion_seleccionada = st.session_state.opcion_seleccionada' not in lines[i]:
            if 'if st.button' in lines[i] and 'key=' in lines[i]:
                # Extraer el nombre de la opción
                nombre = lines[i].split('key="menu_')[-1].split('"')[0]
                # Actualizar la línea con una clave única
                lines[i] = lines[i].replace(
                    f'key="menu_{nombre}"',
                    f'key="menu_{i}_{nombre}"'
                )
            i += 1
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("Claves del menú actualizadas correctamente.")
        return True
        
    except Exception as e:
        print(f"Error al actualizar las claves del menú: {e}")
        return False

if __name__ == "__main__":
    if update_menu_keys():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron actualizar las claves del menú.")
