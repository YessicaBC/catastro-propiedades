# Script para corregir todas las claves de botones duplicadas
def fix_all_buttons():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contador para hacer las claves únicas
        button_counter = 0
        button_keys = set()
        
        # Dividir el contenido en líneas
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Buscar líneas con st.button
            if 'st.button(' in line and 'key=' in line:
                # Extraer la clave actual
                key_start = line.find('key=') + 5  # +5 para saltar 'key="'
                key_end = line.find('"', key_start)
                
                if key_start > 0 and key_end > key_start:
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
        
        # Unir las líneas de nuevo
        new_content = '\n'.join(new_lines)
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Se actualizaron {button_counter} botones con claves duplicadas.")
        return True
        
    except Exception as e:
        print(f"Error al corregir las claves: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando corrección de claves de botones...")
    if fix_all_buttons():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron corregir todas las claves.")
