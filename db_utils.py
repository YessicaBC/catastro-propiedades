import sqlite3
import os
from pathlib import Path
from sqlite3 import Error
import streamlit as st

# Configuración de la base de datos
DB_DIR = Path.home() / '.catastro_propiedades'
DB_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH = str(DB_DIR / 'catastro_propiedades.db')

def get_db_connection():
    """Crea una conexión a la base de datos SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Habilitar claves foráneas
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            
            # Tabla de propiedades
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS propiedades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT NOT NULL,
                propietario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                rol_propiedad TEXT NOT NULL,
                avaluo_total REAL NOT NULL,
                destino_sii TEXT,
                destino_dom TEXT,
                patente_comercial TEXT,
                num_contacto TEXT,
                coordenadas TEXT,
                fiscalizacion_dom TEXT,
                m2_terreno REAL,
                m2_construidos REAL,
                linea_construccion TEXT,
                ano_construccion INTEGER,
                expediente_dom TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(rut, rol_propiedad)
            )
            ''')
            
            # Tabla de fotos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                propiedad_id INTEGER,
                ruta_archivo TEXT NOT NULL,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (propiedad_id) REFERENCES propiedades (id) ON DELETE CASCADE
            )
            ''')
            
            # Crear índices para búsquedas frecuentes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_propiedades_rut ON propiedades(rut)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_propiedades_rol ON propiedades(rol_propiedad)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fotos_propiedad ON fotos(propiedad_id)')
            
            conn.commit()
            return True
            
        except Error as e:
            st.error(f"Error al inicializar la base de datos: {e}")
            return False
        finally:
            conn.close()
    return False
