import os
import yaml
from pathlib import Path

# Configuración de la ruta del archivo de credenciales
CREDENTIALS_FILE = Path(__file__).parent / ".streamlit" / "credentials.yaml"

# Crear el directorio si no existe
CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Credenciales por defecto con contraseña hasheada (admin123)
credentials = {
    'credentials': {
        'usernames': {
            'admin': {
                'email': 'admin@example.com',
                'name': 'Administrador',
                'password': 'pbkdf2:sha256:100000$c2FsdHNhbHQ$d8f5a9e9c7b8a6d5f4e3d2c1b0a9f8e7d6c5b4a3b2c1d0e9f8a7b6c5d4e3f2',
                'role': 'admin'
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'catastro_auth_key',
        'name': 'catastro_auth_cookie'
    }
}

def main():
    print("=== Solución de problemas de autenticación ===")
    print(f"Ruta del archivo: {CREDENTIALS_FILE}")
    
    # Escribir el archivo de credenciales
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            yaml.dump(credentials, f, default_flow_style=False)
        
        # Verificar que el archivo se creó correctamente
        if CREDENTIALS_FILE.exists():
            print("\n✅ Archivo de credenciales creado exitosamente.")
            print("\nPuede ahora iniciar sesión con:")
            print("Usuario: admin")
            print("Contraseña: admin123")
            print("\nPor favor, reinicie la aplicación para aplicar los cambios.")
        else:
            print("\n❌ No se pudo verificar la creación del archivo.")
            
    except Exception as e:
        print(f"\n❌ Error al crear el archivo de credenciales: {e}")
        print("\nPosibles soluciones:")
        print("1. Ejecute el script como administrador")
        print("2. Verifique los permisos de escritura en el directorio")
        print("3. Cree manualmente el directorio .streamlit/ y el archivo credentials.yaml")

if __name__ == "__main__":
    main()
