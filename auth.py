import streamlit as st
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import bcrypt
import os

# Configuración de la ruta del archivo de credenciales
CREDENTIALS_FILE = Path(__file__).parent / ".streamlit" / "credentials.yaml"

# Función para hashear contraseñas con bcrypt
def hash_password(password):
    # Genera un salt y hashea la contraseña
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_credentials(username, password):
    """Verifica las credenciales del usuario"""
    try:
        print(f"\n--- Iniciando verificación de credenciales para: {username} ---")
        print(f"Ruta del archivo de credenciales: {CREDENTIALS_FILE}")
        print(f"¿Existe el archivo?: {CREDENTIALS_FILE.exists()}")
        
        if not CREDENTIALS_FILE.exists():
            print("Error: Archivo de credenciales no encontrado")
            return False, "Error de autenticación: Archivo de credenciales no encontrado"
            
        with open(CREDENTIALS_FILE, 'r') as file:
            config = yaml.load(file, Loader=SafeLoader)
            print("Contenido del archivo de credenciales:", config)
            
        if not config or 'credentials' not in config:
            print("Error: Formato de credenciales inválido")
            return False, "Error de autenticación: Formato de credenciales inválido"
            
        users = config.get('credentials', {}).get('usernames', {})
        print(f"Usuarios encontrados: {list(users.keys())}")
        
        if username not in users:
            print(f"Error: Usuario '{username}' no encontrado")
            return False, "Usuario o contraseña incorrectos"
            
        user_data = users[username]
        stored_hash = user_data.get('password', '').encode('utf-8')
        
        print(f"Verificando contraseña para usuario: {username}")
        print(f"Hash almacenado: {stored_hash}")
        
        # Verificar la contraseña usando bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            print("¡Autenticación exitosa!")
            return True, "Autenticación exitosa"
        else:
            print("Error: Contraseña incorrecta")
            return False, "Contraseña incorrecta"
            
    except Exception as e:
        print(f"Error en check_credentials: {str(e)}")
        return False, f"Error al verificar credenciales: {str(e)}"

def show_login_form():
    """Muestra el formulario de inicio de sesión"""
    with st.sidebar.form("login_form"):
        st.markdown("## Inicio de Sesión")
        username = st.text_input("Usuario", key="login_username")
        password = st.text_input("Contraseña", type="password", key="login_password")
        submitted = st.form_submit_button("Iniciar Sesión")
        
        if submitted and username and password:
            is_valid, message = check_credentials(username, password)
            if is_valid:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                # Cargar datos adicionales del usuario
                with open(CREDENTIALS_FILE, 'r') as file:
                    config = yaml.load(file, Loader=SafeLoader)
                    user_data = config['credentials']['usernames'].get(username, {})
                    st.session_state['name'] = user_data.get('name', username)
                    st.session_state['role'] = user_data.get('role', 'user')
                st.rerun()
            else:
                st.error(message)
                
def check_auth():
    """Verifica si el usuario está autenticado"""
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
        
    if not st.session_state['authentication_status']:
        show_login_form()
        return False, None
        
    return True, st.session_state.get('username')

def logout():
    """Cierra la sesión del usuario"""
    st.session_state['authentication_status'] = False
    st.session_state.pop('username', None)
    st.session_state.pop('name', None)
    st.session_state.pop('role', None)
    st.rerun()

def initialize_authentication():
    """Inicializa el sistema de autenticación"""
    if not CREDENTIALS_FILE.exists():
        # Crear credenciales por defecto
        default_username = 'admin'
        default_password = 'admin123'  # Se hasheará al guardar
        
        default_config = {
            'credentials': {
                'usernames': {
                    default_username: {
                        'email': 'admin@example.com',
                        'name': 'Administrador',
                        'password': hash_password(default_password),
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
        
        # Crear directorio si no existe
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar credenciales por defecto
        with open(CREDENTIALS_FILE, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
            
def register_user(username, password, name, email, role='user'):
    """Registra un nuevo usuario"""
    try:
        # Cargar configuración existente o crear una nueva
        if CREDENTIALS_FILE.exists():
            with open(CREDENTIALS_FILE, 'r') as file:
                config = yaml.load(file, Loader=SafeLoader) or {}
        else:
            config = {}
            
        if 'credentials' not in config:
            config['credentials'] = {}
        if 'usernames' not in config['credentials']:
            config['credentials']['usernames'] = {}
            
        # Verificar si el usuario ya existe
        if username in config['credentials']['usernames']:
            return False, "El nombre de usuario ya está en uso"
            
        # Añadir el nuevo usuario
        config['credentials']['usernames'][username] = {
            'email': email,
            'name': name,
            'password': hash_password(password),
            'role': role
        }
        
        # Asegurar que exista la sección de cookies
        if 'cookie' not in config:
            config['cookie'] = {
                'expiry_days': 30,
                'key': 'catastro_auth_key',
                'name': 'catastro_auth_cookie'
            }
        
        # Guardar la configuración actualizada
        with open(CREDENTIALS_FILE, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
            
        return True, "Usuario registrado exitosamente"
        
    except Exception as e:
        return False, f"Error al registrar el usuario: {str(e)}"

def update_user_profile(current_username, new_username=None, new_password=None, new_role=None, new_name=None, new_email=None):
    """
    Actualiza el perfil de un usuario existente.
    
    Args:
        current_username (str): Nombre de usuario actual
        new_username (str, opcional): Nuevo nombre de usuario
        new_password (str, opcional): Nueva contraseña (sin hashear)
        new_role (str, opcional): Nuevo rol
        new_name (str, opcional): Nuevo nombre completo
        new_email (str, opcional): Nuevo correo electrónico
        
    Returns:
        tuple: (success, message) donde success es un booleano que indica si la operación fue exitosa
    """
    try:
        # Cargar configuración actual
        if not CREDENTIALS_FILE.exists():
            return False, "Archivo de credenciales no encontrado"
            
        with open(CREDENTIALS_FILE, 'r') as file:
            config = yaml.load(file, Loader=SafeLoader)
            
        if not config or 'credentials' not in config or 'usernames' not in config['credentials']:
            return False, "Formato de credenciales inválido"
            
        users = config['credentials']['usernames']
        
        # Verificar que el usuario actual existe
        if current_username not in users:
            return False, "Usuario no encontrado"
            
        user_data = users[current_username]
        
        # Actualizar nombre de usuario si es necesario
        if new_username and new_username != current_username:
            if new_username in users:
                return False, "El nuevo nombre de usuario ya está en uso"
            users[new_username] = users.pop(current_username)
            current_username = new_username
            
        # Actualizar contraseña si se proporciona
        if new_password:
            users[current_username]['password'] = hash_password(new_password)
            
        # Actualizar rol si se proporciona
        if new_role:
            users[current_username]['role'] = new_role
            
        # Actualizar nombre si se proporciona
        if new_name:
            users[current_username]['name'] = new_name
            
        # Actualizar email si se proporciona
        if new_email:
            users[current_username]['email'] = new_email
        
        # Guardar los cambios
        with open(CREDENTIALS_FILE, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
            
        # Actualizar la sesión si el usuario actualizó su propio perfil
        if 'username' in st.session_state and st.session_state['username'] == current_username:
            if new_username:
                st.session_state['username'] = new_username
            if new_name:
                st.session_state['name'] = new_name
            if new_role:
                st.session_state['role'] = new_role
                
        return True, "Perfil actualizado exitosamente"
        
    except Exception as e:
        return False, f"Error al actualizar el perfil: {str(e)}"
