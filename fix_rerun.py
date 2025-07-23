# Script para reemplazar st.experimental_rerun() por st.rerun()

# Ruta del archivo a modificar
file_path = r'c:\Users\YBUSTAMANTEC\Desktop\catastro-propiedades\app.py'

# Leer el contenido del archivo
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Reemplazar todas las ocurrencias
new_content = content.replace('st.experimental_rerun()', 'st.rerun()')

# Escribir el contenido actualizado
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print("Reemplazo completado exitosamente.")
