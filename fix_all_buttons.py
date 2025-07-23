# Script para corregir todas las claves de botones duplicadas
def fix_all_buttons():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Contador para hacer las claves únicas
        button_counter = 0
        button_keys = set()
        
        # Lista para almacenar las nuevas líneas
        new_lines = []
        
        for line in lines:
            # Buscar líneas con st.button
            if 'st.button(' in line and 'key=' in line:
                # Extraer la clave actual
                key_start = line.find('key=') + 5  # +5 para saltar 'key="'
                key_end = line.find('"', key_start)
                key_value = line[key_start:key_end]
                
                # Si la clave ya existe, generamos una nueva
                if key_value in button_keys:
                    new_key = f"{key_value}_{button_counter}"
                    line = line.replace(f'key="{key_value}"', f'key="{new_key}"')
                    button_counter += 1
                    print(f"Clave duplicada encontrada: {key_value} -> {new_key}")
                else:
                    button_keys.add(key_value)
            
            new_lines.append(line)
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"Se actualizaron {button_counter} botones con claves duplicadas.")
        return True
        
    except Exception as e:
        print(f"Error al corregir las claves: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando corrección de claves de botones...")
    if fix_all_buttons():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron corregir todas las claves.")
