import os
import shutil
from datetime import datetime
from pathlib import Path
import sqlite3

def crear_backup_db(ruta_db, directorio_backup='backups'):
    """
    Crea una copia de seguridad de la base de datos SQLite.
    
    Args:
        ruta_db (str): Ruta al archivo de base de datos.
        directorio_backup (str): Directorio donde se guardarán los backups.
    
    Returns:
        str: Ruta al archivo de backup creado o None si hubo un error.
    """
    try:
        # Crear directorio de backups si no existe
        Path(directorio_backup).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo con marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_backup = f"backup_{timestamp}.db"
        ruta_backup = os.path.join(directorio_backup, nombre_backup)
        
        # Cerrar todas las conexiones existentes
        conexiones_cerradas = False
        try:
            # Intentar cerrar conexiones
            conexion = sqlite3.connect(ruta_db)
            conexion.close()
            conexiones_cerradas = True
        except:
            pass
        
        if conexiones_cerradas:
            # Crear copia del archivo
            shutil.copy2(ruta_db, ruta_backup)
            return ruta_backup
        else:
            print("No se pudieron cerrar las conexiones a la base de datos")
            return None
            
    except Exception as e:
        print(f"Error al crear backup: {e}")
        return None

def programar_backup_diario():
    """Programa un backup diario de la base de datos"""
    try:
        # Verificar si ya se hizo backup hoy
        hoy = datetime.now().strftime("%Y%m%d")
        backup_hoy = f"backup_{hoy}_"
        directorio_backup = 'backups'
        
        # Verificar si ya existe un backup de hoy
        if os.path.exists(directorio_backup):
            archivos = os.listdir(directorio_backup)
            if not any(archivo.startswith(backup_hoy) for archivo in archivos):
                # No hay backup hoy, crear uno
                return crear_backup_db('catastro_propiedades.db', directorio_backup)
        else:
            # No existe el directorio de backups, crear uno
            return crear_backup_db('catastro_propiedades.db', directorio_backup)
            
    except Exception as e:
        print(f"Error en programación de backup: {e}")
        return None
