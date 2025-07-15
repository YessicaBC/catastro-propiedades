import json
import os
from pathlib import Path

# Ruta al archivo de configuración
CONFIG_DIR = Path(".config")
CONFIG_FILE = CONFIG_DIR / "app_config.json"

# Configuración por defecto
DEFAULT_CONFIG = {
    "tema": "claro",  # 'claro' o 'oscuro'
    "ultima_vista": "Inicio",
    "items_por_pagina": 10,
    "mostrar_tutorial": True,
    "configuracion_mapa": {
        "zoom_inicial": 14,
        "tipo_mapa": "OpenStreetMap",
        "mostrar_marcadores": True
    }
}

def asegurar_directorio_config():
    """Asegura que el directorio de configuración exista"""
    CONFIG_DIR.mkdir(exist_ok=True)

def cargar_configuracion():
    """Carga la configuración desde el archivo o crea una nueva con valores por defecto"""
    asegurar_directorio_config()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Combinar con la configuración por defecto para asegurar que no falten claves
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            print(f"Error al cargar la configuración: {e}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

guardar_configuracion = lambda config: CONFIG_FILE.write_text(json.dumps(config, indent=4, ensure_ascii=False), encoding='utf-8')

def actualizar_configuracion(nuevos_valores):
    """Actualiza la configuración con nuevos valores"""
    config = cargar_configuracion()
    config.update(nuevos_valores)
    guardar_configuracion(config)
    return config

def obtener_valor(clave, valor_por_defecto=None):
    """Obtiene un valor específico de la configuración"""
    config = cargar_configuracion()
    return config.get(clave, valor_por_defecto if valor_por_defecto is not None else DEFAULT_CONFIG.get(clave))

def reiniciar_configuracion():
    """Reinicia la configuración a los valores por defecto"""
    guardar_configuracion(DEFAULT_CONFIG)
    return DEFAULT_CONFIG
