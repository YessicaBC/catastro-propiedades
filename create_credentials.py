import os
import yaml
from pathlib import Path

# Configuración de la ruta del archivo de credenciales
CREDENTIALS_FILE = Path(__file__).parent / ".streamlit" / "credentials.yaml"

# Crear el directorio si no existe
CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Credenciales por defecto
credentials = {
    'credentials': {
        'usernames': {
            'admin': {
                'email': 'admin@example.com',
                'name': 'Administrador',
                'password': 'hashed_password_here',  # Se reemplazará con el hash real
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

def hash_password(password):
    """Genera un hash seguro de la contraseña."""
    import hashlib
    import base64
    import os
    
    # Generar una sal aleatoria
    salt = os.urandom(16)
    
    # Crear el hash con PBKDF2
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Número de iteraciones
    )
    
    # Devolver el hash en formato string
    return f"pbkdf2:sha256:100000${salt.hex()}${dk.hex()}"

def main():
    print("=== Creación de archivo de credenciales ===")
    print(f"Ruta del archivo: {CREDENTIALS_FILE}")
    
    # Verificar si el archivo ya existe
    if CREDENTIALS_FILE.exists():
        print("\n⚠️  El archivo de credenciales ya existe.")
        response = input("¿Desea sobrescribirlo? (s/n): ")
        if response.lower() != 's':
            print("Operación cancelada.")
            return
    
    # Solicitar contraseña para el usuario admin
    while True:
        password = input("\nIngrese la contraseña para el usuario 'admin': ")
        if not password:
            print("La contraseña no puede estar vacía.")
            continue
        confirm = input("Confirme la contraseña: ")
        if password == confirm:
            break
        print("Las contraseñas no coinciden. Intente de nuevo.")
    
    # Generar el hash de la contraseña
    hashed_password = hash_password(password)
    credentials['credentials']['usernames']['admin']['password'] = hashed_password
    
    # Escribir el archivo
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            yaml.dump(credentials, f, default_flow_style=False)
        
        print(f"\n✅ Archivo de credenciales creado exitosamente en: {CREDENTIALS_FILE}")
        print("\nPuede ahora iniciar sesión con:")
        print(f"Usuario: admin")
        print(f"Contraseña: {password}")
        
    except Exception as e:
        print(f"\n❌ Error al crear el archivo de credenciales: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que tienes permisos de escritura en el directorio.")
        print("2. Intenta ejecutar el script como administrador.")
        print("3. Crea manualmente el directorio .streamlit/ y establece los permisos adecuados.")

if __name__ == "__main__":
    main()
