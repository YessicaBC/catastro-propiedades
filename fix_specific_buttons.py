# Script para corregir las claves de botones específicas
def fix_specific_buttons():
    try:
        # Leer el contenido actual
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Contador para hacer las claves únicas
        button_counter = 0
        
        # Diccionario para rastrear las claves existentes
        existing_keys = {}
        
        # Lista para almacenar las nuevas líneas
        new_lines = []
        
        for line in lines:
            # Buscar líneas con st.button
            if 'st.button(' in line and 'key=' in line:
                # Extraer la clave actual
                key_start = line.find('key=') + 5  # +5 para saltar 'key="'
                key_end = line.find('"', key_start)
                
                if key_start > 0 and key_end > key_start:
                    key_value = line[key_start:key_end]
                    
                    # Si la clave ya existe en el diccionario, generamos una nueva
                    if key_value in existing_keys:
                        existing_keys[key_value] += 1
                        new_key = f"{key_value}_{existing_keys[key_value]}"
                        line = line.replace(f'key="{key_value}"', f'key="{new_key}"')
                        print(f"Clave duplicada encontrada: {key_value} -> {new_key}")
                    else:
                        existing_keys[key_value] = 0
            
            new_lines.append(line)
        
        # Guardar los cambios
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"Se actualizaron {sum(1 for v in existing_keys.values() if v > 0)} botones con claves duplicadas.")
        return True
        
    except Exception as e:
        print(f"Error al corregir las claves: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando corrección de claves de botones específicas...")
    if fix_specific_buttons():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudieron corregir las claves.")
