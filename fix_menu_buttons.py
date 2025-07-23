# Script para corregir las claves de los botones del menú
def fix_menu_buttons():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contador para hacer las claves únicas
        button_counter = 0
        
        # Dividir el contenido en líneas
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Buscar líneas con st.button en el menú
            if 'st.button' in line and 'key="menu_' in line:
                # Extraer el nombre de la opción
                nombre_start = line.find('key="menu_') + 10  # +10 para saltar 'key="menu_'
                nombre_end = line.find('"', nombre_start)
                nombre = line[nombre_start:nombre_end]
                
                # Crear una nueva clave única
                new_key = f"menu_btn_{button_counter}_{nombre}"
                
                # Reemplazar la clave antigua con la nueva
                line = line.replace(f'key="menu_{nombre}"', f'key="{new_key}"')
                button_counter += 1
            
            new_lines.append(line)
        
        # Unir las líneas de nuevo
        new_content = '\n'.join(new_lines)
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Se actualizaron {button_counter} botones del menú con claves únicas.")
        return True
        
    except Exception as e:
        print(f"Error al corregir las claves de los botones: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando corrección de claves de botones del menú...")
    if fix_menu_buttons():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron corregir las claves de los botones.")
