// Función para expandir el contenido principal
function expandirContenido(expandir) {
    const mainContent = document.querySelector('.main');
    const sidebar = document.querySelector('.sidebar');
    const volverMenu = document.getElementById('volver-menu');
    
    if (expandir) {
        document.body.classList.add('sidebar-collapsed');
        if (mainContent) mainContent.classList.add('main-content-expanded');
        if (volverMenu) volverMenu.style.display = 'block';
        
        // Desplazar al inicio del contenido
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        document.body.classList.remove('sidebar-collapsed');
        if (mainContent) mainContent.classList.remove('main-content-expanded');
        if (volverMenu) volverMenu.style.display = 'none';
    }
    
    // Ajustar el padding del contenido principal
    const header = document.querySelector('.stApp > div:first-child');
    if (header) {
        header.style.paddingLeft = expandir ? '2rem' : '1rem';
        header.style.paddingRight = expandir ? '2rem' : '1rem';
    }
}

// Manejar clics en los botones del menú de Streamlit
function manejarClicMenu(e) {
    const boton = e.target.closest('.stButton > button');
    if (!boton) return;
    
    // Obtener el texto del botón
    const textoBoton = boton.textContent.trim();
    
    // Si no es el botón de Inicio, expandir el contenido
    if (textoBoton !== '🏠 Inicio') {
        e.preventDefault();
        expandirContenido(true);
        
        // Aquí puedes agregar lógica para cargar el contenido dinámico
        // basado en el texto del botón
        console.log(`Cargando vista de: ${textoBoton}`);
    } else {
        // Si es el botón de Inicio, contraer el contenido
        expandirContenido(false);
    }
}

// Inicializar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Agregar manejador de eventos al contenedor de la barra lateral
    const sidebar = document.querySelector('.sidebar .sidebar-content');
    if (sidebar) {
        sidebar.addEventListener('click', manejarClicMenu);
    }
    
    // Cerrar menú en móviles
    if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.remove('active');
    }
    
    // Botón para volver al menú
    document.addEventListener('click', function(e) {
        if (e.target.closest('.volver-menu')) {
            expandirContenido(false);
        }
    });
});
