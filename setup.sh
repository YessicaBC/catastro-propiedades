#!/bin/bash

# Este script se puede usar para configurar variables de entorno en Heroku
# Uso: heroku config:set $(cat setup.sh | xargs)

# Configuración de la aplicación
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
