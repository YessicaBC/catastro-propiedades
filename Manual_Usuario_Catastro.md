# Manual de Usuario
# Aplicación de Catastro de Propiedades

![Logo](https://www.svgrepo.com/show/530661/land-management.svg)

**Versión 1.0**  
**Mayo 2025**

---

## Índice

1. [Introducción](#1-introducción)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [Acceso a la Aplicación](#3-acceso-a-la-aplicación)
4. [Interfaz Principal](#4-interfaz-principal)
5. [Funcionalidades](#5-funcionalidades)
   - [5.1 Agregar Propiedad](#51-agregar-propiedad)
   - [5.2 Lista de Propiedades](#52-lista-de-propiedades)
   - [5.3 Buscar Propiedades](#53-buscar-propiedades)
   - [5.4 Exportar Datos](#54-exportar-datos)
   - [5.5 Visualización en Mapa](#55-visualización-en-mapa)
   - [5.6 Estadísticas](#56-estadísticas)
6. [Guía Paso a Paso](#6-guía-paso-a-paso)
7. [Solución de Problemas](#7-solución-de-problemas)
8. [Contacto y Soporte](#8-contacto-y-soporte)

---

## 1. Introducción

La Aplicación de Catastro de Propiedades es una herramienta diseñada para gestionar y visualizar información de propiedades en la comuna. Permite registrar, editar y visualizar datos de propiedades, incluyendo su ubicación en el mapa y estado de fiscalización.

Esta aplicación facilita el trabajo de los funcionarios municipales encargados del catastro, permitiendo un acceso rápido y eficiente a la información de las propiedades.

---

## 2. Requisitos del Sistema

Para utilizar la aplicación, se requiere:

- **Navegador web**: Chrome, Firefox, Safari o Edge (versiones actualizadas)
- **Conexión a Internet**: Para acceder a la aplicación y visualizar mapas
- **Resolución de pantalla**: Mínimo 1024x768 (recomendado 1920x1080)

---

## 3. Acceso a la Aplicación

Para acceder a la aplicación:

1. Abra su navegador web
2. Ingrese la dirección URL proporcionada
3. La aplicación se cargará automáticamente

**Nota**: No se requiere inicio de sesión para acceder a la aplicación.

---

## 4. Interfaz Principal

La interfaz de la aplicación está organizada en:

- **Barra lateral (izquierda)**: Menú de navegación principal
- **Área principal (derecha)**: Contenido según la opción seleccionada
- **Encabezado**: Título de la sección actual

![Interfaz Principal](https://i.imgur.com/example1.png)

---

## 5. Funcionalidades

### 5.1 Agregar Propiedad

Esta función permite registrar nuevas propiedades en el sistema.

**Campos disponibles**:

| Campo | Descripción | Formato |
|-------|-------------|---------|
| RUT | RUT del propietario | 12.345.678-9 |
| Propietario | Nombre completo | Texto |
| Dirección | Ubicación de la propiedad | Texto |
| ROL | Identificador único | Texto |
| Avalúo Total | Valor fiscal | Número |
| Destino SII | Clasificación SII | Texto |
| Destino según Terreno | Uso actual | Texto |
| Destino DOM | Clasificación DOM | Texto |
| N° en Terreno | Numeración | Texto |
| Coordenadas | Ubicación geográfica | Latitud, Longitud |
| Fiscalizada DOM | Estado de fiscalización | CERRADA / SIN PATENTE AL DIA / CON PATENTE AL DIA / VIVIENDA COLECTIVA / SIN INFORMACION |
| M2 Terreno | Superficie del terreno | Número |
| M2 Construidos | Superficie construida | Número |
| Línea de Construcción | Información técnica | Texto |
| Año de Construcción | Año de edificación | Número |
| Expediente DOM | Referencia | Texto |
| Observaciones | Notas adicionales | Texto largo |

**Validaciones**:
- El RUT debe ser válido según algoritmo chileno
- Las coordenadas deben tener formato correcto (latitud, longitud)

---

### 5.2 Lista de Propiedades

Muestra todas las propiedades registradas en el sistema.

**Características**:
- Vista en tabla con todas las propiedades
- Edición directa de datos
- Ordenamiento por columnas
- Paginación para grandes volúmenes de datos

---

### 5.3 Buscar Propiedades

Permite filtrar propiedades según diferentes criterios.

**Opciones de búsqueda**:
- Por RUT
- Por Propietario
- Por Dirección
- Por ROL

**Funcionamiento**:
1. Ingrese el texto a buscar
2. La tabla se filtrará automáticamente
3. Los resultados mostrarán coincidencias parciales

---

### 5.4 Exportar Datos

Permite descargar los datos en formato Excel.

**Pasos**:
1. En la vista de tabla, haga clic en "Exportar a Excel"
2. Seleccione la ubicación para guardar el archivo
3. El archivo se descargará con todas las propiedades y sus datos

---

### 5.5 Visualización en Mapa

Muestra la ubicación geográfica de las propiedades.

**Características**:
- Mapa interactivo centrado en la comuna
- Marcadores para cada propiedad con coordenadas
- Información detallada al hacer clic en los marcadores
- Vista previa al agregar nuevas propiedades

**Leyenda de marcadores**:
- 🔵 Azul: Propiedades existentes
- 🔴 Rojo: Nueva propiedad (en formulario)

---

### 5.6 Estadísticas

Muestra gráficos y métricas sobre las propiedades registradas.

**Información disponible**:
- Distribución de estados de fiscalización
- Porcentajes por categoría
- Total de propiedades por estado

**Categorías de fiscalización**:
- CERRADA (🟧 Naranja)
- SIN PATENTE AL DIA (🔴 Rojo)
- CON PATENTE AL DIA (🟢 Verde)
- VIVIENDA COLECTIVA (🔵 Azul)
- SIN INFORMACION (⚫ Gris)

---

## 6. Guía Paso a Paso

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
3. Para editar, haga clic directamente en la celda que desea modificar

### Exportar Datos

1. En la vista de tabla
2. Haga clic en el botón "Exportar a Excel"
3. Seleccione la ubicación para guardar el archivo

---

## 7. Solución de Problemas

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| No se visualiza el mapa | Problemas de conexión | Verifique su conexión a Internet |
| Error al ingresar coordenadas | Formato incorrecto | Use formato: latitud, longitud (ej: -33.4172, -70.6506) |
| No se guardan los cambios | Error de sesión | Actualice la página y vuelva a intentarlo |
| No se puede exportar a Excel | Problema temporal | Intente nuevamente en unos minutos |

---

## 8. Contacto y Soporte

Para consultas o soporte técnico:

- **Correo electrónico**: soporte@catastro.cl
- **Teléfono**: (2) 2345 6789
- **Horario de atención**: Lunes a Viernes, 9:00 - 18:00 hrs.

---

*Este manual fue creado en Mayo 2025.*  
*Última actualización: 15 de Mayo, 2025*
