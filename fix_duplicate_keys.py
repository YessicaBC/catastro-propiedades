# Script para corregir claves duplicadas en los botones
def fix_duplicate_keys():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Contador para hacer las claves únicas
        button_counter = 0
        
        # Lista para almacenar las nuevas líneas
        new_lines = []
        
        for line in lines:
            # Buscar líneas con st.button
            if 'st.button' in line and 'key=' in line:
                # Incrementar el contador para hacer la clave única
                button_counter += 1
                
                # Extraer la parte de la clave
                key_start = line.find('key=') + 5  # +5 para saltar 'key="'
                key_end = line.find('"', key_start)
                key_value = line[key_start:key_end]
                
                # Si la clave no tiene un sufijo numérico, agregar uno
                if not key_value.replace('_', '').isnumeric() and not key_value.endswith(str(button_counter)):
                    new_key = f"{key_value}_{button_counter}"
                    line = line.replace(f'key="{key_value}"', f'key="{new_key}"')
            
            new_lines.append(line)
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"Se actualizaron {button_counter} botones con claves únicas.")
        return True
        
    except Exception as e:
        print(f"Error al corregir las claves: {e}")
        return False

if __name__ == "__main__":
    if fix_duplicate_keys():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron corregir las claves.")
