import os
from notion_client import Client

# Para usar la API de Notion, necesitas un token de integración
# Puedes obtenerlo en https://www.notion.so/my-integrations
NOTION_TOKEN = "tu_token_secreto_aquí"  # Reemplaza con tu token real

# Inicializa el cliente
notion = Client(auth=NOTION_TOKEN)

def listar_bases_de_datos():
    """Lista todas las bases de datos a las que tiene acceso la integración."""
    response = notion.search(filter={"property": "object", "value": "database"})
    
    print("Bases de datos disponibles:")
    for db in response["results"]:
        print(f"- {db['title'][0]['plain_text'] if db.get('title') and len(db['title']) > 0 else 'Sin título'} (ID: {db['id']})")
    
    return response["results"]

def crear_pagina_en_db(database_id, propiedades):
    """
    Crea una nueva página (entrada) en una base de datos de Notion.
    
    Args:
        database_id: ID de la base de datos
        propiedades: Diccionario con las propiedades a establecer
    """
    nueva_pagina = notion.pages.create(
        parent={"database_id": database_id},
        properties=propiedades
    )
    
    print(f"Página creada con ID: {nueva_pagina['id']}")
    return nueva_pagina

def ejemplo_crear_propiedad():
    """Ejemplo de cómo crear una entrada de propiedad en una base de datos."""
    # Reemplaza con el ID de tu base de datos
    DATABASE_ID = "tu_database_id_aquí"
    
    # Ejemplo de propiedades para una propiedad
    propiedades = {
        "Propietario": {
            "title": [
                {
                    "text": {
                        "content": "Juan Pérez"
                    }
                }
            ]
        },
        "Dirección": {
            "rich_text": [
                {
                    "text": {
                        "content": "Calle Principal 123, Independencia"
                    }
                }
            ]
        },
        "ROL": {
            "rich_text": [
                {
                    "text": {
                        "content": "123-456"
                    }
                }
            ]
        },
        "Avalúo Total": {
            "number": 45000000
        },
        "Estado de Fiscalización": {
            "select": {
                "name": "CON PATENTE AL DIA"
            }
        }
    }
    
    return crear_pagina_en_db(DATABASE_ID, propiedades)

if __name__ == "__main__":
    # Primero lista las bases de datos disponibles
    listar_bases_de_datos()
    
    # Descomentar para crear una propiedad de ejemplo
    # ejemplo_crear_propiedad()
