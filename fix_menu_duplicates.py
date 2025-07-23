# Script para corregir las claves duplicadas en el menú

def fix_menu_duplicates():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar cuántas veces aparece el menú
        menu_count = content.count('# Menú de navegación\nwith st.sidebar:')
        
        if menu_count <= 1:
            print("No se encontraron menús duplicados.")
            return False
            
        # Encontrar la posición del primer menú
        first_menu_start = content.find('# Menú de navegación\nwith st.sidebar:')
        first_menu_end = content.find('# Contenido principal basado en la opción seleccionada', first_menu_start)
        
        if first_menu_start == -1 or first_menu_end == -1:
            print("No se pudo encontrar la estructura del menú.")
            return False
            
        # Extraer el primer menú
        first_menu = content[first_menu_start:first_menu_end]
        
        # Reemplazar todos los menús por el primero
        content = content.replace('# Menú de navegación\nwith st.sidebar:', '### MENU_REMOVED ###')
        content = content.replace('### MENU_REMOVED ###', first_menu, 1)
        
        # Eliminar los menús restantes
        content = content.replace('### MENU_REMOVED ###', '')
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Se eliminaron {menu_count-1} menús duplicados.")
        return True
        
    except Exception as e:
        print(f"Error al corregir el menú: {e}")
        return False

if __name__ == "__main__":
    if fix_menu_duplicates():
        print("Menú corregido exitosamente.")
    else:
        print("No se pudo corregir el menú.")
