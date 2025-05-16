# Aplicación de Catastro de Propiedades

Bienvenido a la Aplicación de Catastro de Propiedades, una herramienta integral para la gestión y visualización de información de propiedades en la comuna. Esta aplicación permite registrar, editar, visualizar y exportar datos de propiedades, incluyendo su ubicación geográfica y estado de fiscalización.

## Características Principales

- **Registro de Propiedades**: Formulario completo con validación de datos
- **Visualización en Mapa**: Ubicación geográfica de las propiedades
- **Gestión de Fotos**: Almacenamiento y visualización de imágenes
- **Exportación de Datos**: Soporte para Excel, CSV y JSON
- **Búsqueda y Filtrado**: Búsqueda avanzada de propiedades
- **Panel de Control**: Estadísticas y métricas clave

## Requisitos del Sistema

- Python 3.8 o superior
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexión a Internet (para mapas y geolocalización)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/catastro-propiedades.git
   cd catastro-propiedades
   ```

2. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Copiar el archivo de configuración de ejemplo:
   ```bash
   cp .env.example .env
   ```

2. Configurar las variables de entorno en `.env` según sea necesario.

## Uso

Para iniciar la aplicación localmente:

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## Despliegue en Heroku

1. Instalar Heroku CLI
2. Iniciar sesión:
   ```bash
   heroku login
   ```
3. Crear una nueva aplicación:
   ```bash
   heroku create nombre-de-tu-app
   ```
4. Desplegar:
   ```bash
   git push heroku main
   ```

## Estructura del Proyecto

```
catastro-propiedades/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── Procfile              # Configuración de Heroku
├── runtime.txt           # Versión de Python
├── .gitignore
├── README.md
├── static/               # Archivos estáticos
└── uploads/              # Archivos subidos por los usuarios
```

## Contribución

Las contribuciones son bienvenidas. Por favor, lee nuestras pautas de contribución antes de enviar pull requests.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte, por favor abra un issue en el repositorio o contacte al equipo de desarrollo.

#### Mapa de Propiedades (🗺️)
- Visualizar ubicación de todas las propiedades
- Ver información al hacer clic en los marcadores
- Vista previa al agregar nuevas propiedades

#### Estadísticas (📈)
- Gráfico de distribución de estados de fiscalización
- Métricas detalladas por categoría
- Porcentajes y totales

### 3. Estados de Fiscalización
- CERRADA
- SIN PATENTE AL DIA
- CON PATENTE AL DIA
- VIVIENDA COLECTIVA
- SIN INFORMACION

## Guía Paso a Paso

### Agregar una Nueva Propiedad
1. Haga clic en "Agregar Propiedad" en el menú lateral
2. Complete el formulario:
   - Ingrese el RUT (se validará automáticamente)
   - Complete los datos de la propiedad
   - Ingrese las coordenadas (formato: latitud, longitud)
   - Seleccione el estado de fiscalización
3. Haga clic en "Guardar" para registrar la propiedad

### Visualizar y Editar Datos
1. Seleccione "Lista de Propiedades" en el menú lateral
2. Use las pestañas para cambiar entre vistas:
   - 📋 Tabla: para editar datos
   - 🗺️ Mapa: para ver ubicaciones
   - 📈 Estadísticas: para ver distribución

### Exportar Datos
1. En la vista de tabla
2. Haga clic en el botón "Exportar a Excel"
3. Seleccione la ubicación para guardar el archivo

## Preguntas Frecuentes

### ¿Cómo ingreso coordenadas?
Las coordenadas deben ingresarse en formato decimal: latitud, longitud
Ejemplo: -33.4172, -70.6506

### ¿Cómo edito una propiedad?
Los datos pueden editarse directamente en la tabla de datos. Los cambios se guardan automáticamente.

### ¿Se pueden buscar propiedades?
Sí, use el campo de búsqueda en la tabla para filtrar por cualquier campo (RUT, Propietario, Dirección, etc.).

### ¿Cómo actualizo el estado de fiscalización?
1. Encuentre la propiedad en la tabla
2. Haga clic en el campo de estado
3. Seleccione el nuevo estado de la lista desplegable
