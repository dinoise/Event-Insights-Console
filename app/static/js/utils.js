// Función auxiliar para obtener cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Función auxiliar para mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed-top mx-auto mt-3`;
    notification.style.width = '300px';
    notification.style.zIndex = '1100';
    notification.style.left = '50%';
    notification.style.transform = 'translateX(-50%)';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

export { getCookie, showNotification }