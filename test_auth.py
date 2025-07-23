import os
import sys
import yaml
from pathlib import Path

# Add the current directory to the path so we can import auth
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auth import initialize_authentication, CREDENTIALS_FILE

def check_credentials_file():
    print("=== Verificando archivo de credenciales ===")
    print(f"Ruta del archivo: {CREDENTIALS_FILE}")
    
    # Check if the file exists
    if not CREDENTIALS_FILE.exists():
        print("❌ El archivo de credenciales NO existe.")
        return False
    
    print("✅ El archivo de credenciales existe.")
    
    # Check file permissions
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            content = f.read()
        print("✅ Se puede leer el archivo de credenciales.")
    except Exception as e:
        print(f"❌ No se puede leer el archivo: {e}")
        return False
    
    # Check if the content is valid YAML
    try:
        config = yaml.safe_load(content)
        print("✅ El archivo tiene un formato YAML válido.")
        
        # Check the basic structure
        if not isinstance(config, dict):
            print("❌ El contenido no es un diccionario.")
            return False
            
        if 'credentials' not in config:
            print("❌ No se encontró la clave 'credentials'.")
            return False
            
        if 'usernames' not in config['credentials']:
            print("❌ No se encontró la clave 'usernames' en 'credentials'.")
            return False
            
        print("✅ La estructura del archivo es correcta.")
        print("\nUsuarios encontrados:")
        
        for username, user_data in config['credentials']['usernames'].items():
            print(f"\nUsuario: {username}")
            print(f"  - Nombre: {user_data.get('name', 'No especificado')}")
            print(f"  - Email: {user_data.get('email', 'No especificado')}")
            print(f"  - Rol: {user_data.get('role', 'No especificado')}")
            print(f"  - Contraseña: {'*****' if 'password' in user_data else 'No definida'}")
            
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Error al analizar el archivo YAML: {e}")
        return False

def main():
    print("=== Inicializando autenticación ===")
    try:
        authenticator = initialize_authentication()
        print("✅ Autenticación inicializada correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la autenticación: {e}")
        return
    
    print("\n=== Verificando archivo de credenciales ===")
    if not check_credentials_file():
        print("\n⚠️ Se detectaron problemas con el archivo de credenciales.")
        print("Intentando forzar la creación de un nuevo archivo...")
        
        try:
            # Try to force create the credentials file
            credentials_dir = CREDENTIALS_FILE.parent
            credentials_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a basic credentials file
            default_creds = {
                'credentials': {
                    'usernames': {
                        'admin': {
                            'email': 'admin@example.com',
                            'name': 'Administrador',
                            'password': 'hashed_password_here',
                            'role': 'admin'
                        }
                    }
                },
                'cookie': {
                    'expiry_days': 30,
                    'key': 'catastro_auth_key',
                    'name': 'catastro_auth_cookie'
                },
                'preauthorized': {
                    'emails': []
                }
            }
            
            with open(CREDENTIALS_FILE, 'w') as f:
                yaml.dump(default_creds, f, default_flow_style=False)
                
            print(f"✅ Se creó un nuevo archivo de credenciales en: {CREDENTIALS_FILE}")
            
            # Try to initialize authentication again
            print("\n=== Intentando inicializar autenticación de nuevo ===")
            try:
                authenticator = initialize_authentication()
                print("✅ Autenticación inicializada correctamente después de crear el archivo.")
                
                # Verify the file was created correctly
                print("\n=== Verificando el nuevo archivo de credenciales ===")
                check_credentials_file()
                
            except Exception as e:
                print(f"❌ Error al inicializar la autenticación después de crear el archivo: {e}")
                
        except Exception as e:
            print(f"❌ No se pudo crear el archivo de credenciales: {e}")
            print("\nPosibles soluciones:")
            print("1. Verifica los permisos de escritura en el directorio.")
            print("2. Intenta ejecutar el script como administrador.")
            print("3. Crea manualmente el archivo .streamlit/credentials.yaml con la estructura adecuada.")

if __name__ == "__main__":
    main()
