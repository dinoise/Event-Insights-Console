document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = new bootstrap.Modal('#deleteMappingModal');
    let currentMappingId = null;
    
    // Manejar clic en botones de borrado
    document.querySelectorAll('.delete-mapping').forEach(btn => {
        btn.addEventListener('click', function() {
            currentMappingId = this.dataset.mappingId;
            deleteModal.show();
        });
    });
    
    // Confirmar borrado
    document.getElementById('confirm-delete-mapping').addEventListener('click', function() {
        if (currentMappingId) {
            deleteMapping(currentMappingId)
                .then(() => {
                    deleteModal.hide();
                    // Eliminar la fila de la tabla
                    document.querySelector(`tr[data-mapping-id="${currentMappingId}"]`).remove();
                    // Mostrar notificación
                    showAlert('Mapping deleted successfully', 'success');
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Error deleting mapping: ' + error.message, 'danger');
                });
        }
    });
    
    // Función para borrar el mapeo
    async function deleteMapping(mappingId) {
        const response = await fetch(`/api/event-mapping/${mappingId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Asegúrate de tener esta función
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete mapping');
        }
        
        return await response.json();
    }
    
    // Función para mostrar notificaciones
    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
        alert.style.zIndex = '1100';
        alert.textContent = message;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }
    
    // Función para obtener cookies (simplificada)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});
