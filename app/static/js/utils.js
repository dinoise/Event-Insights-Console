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

// Validando si el dataset o la tabla de bigquery existen
async function validateBQ({ dataset, table = null }) {
    if (!dataset) {
        throw new Error('Dataset es obligatorio para validación');
    }
    
    const response = await fetch('/api/event-mapping/validate-bq', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrf_token')
        },
        body: JSON.stringify({
            dataset: dataset,
            table: table
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Error en validación');
    }
    
    const response_json = await response.json();

    const data = response_json.data
    return data.valid;
}

export { getCookie, showNotification, validateBQ }