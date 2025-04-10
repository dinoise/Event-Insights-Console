import { getCookie, showNotification, validateBQ } from './utils.js'

document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = new bootstrap.Modal('#deleteTypeModal');
    const deleteBtn = document.querySelectorAll('.delete-type');
    const confirmDeleteBtn = document.getElementById('confirm-delete-type')

    let currentType = null;
    
    // Botones
    deleteBtn.forEach(btn => {
        btn.addEventListener('click', function() {
            currentType = this.dataset.typeId;
            console.log(currentType)
            deleteModal.show();
        });
    });

    confirmDeleteBtn.addEventListener('click', function() {
        if (!currentType) {
            return
        }

        deleteType(currentType)
            .then(() => {
                deleteModal.hide();
                // Eliminar la fila de la tabla
                document.querySelector(`tr[data-type-id="${currentType}"]`).remove();
                // Mostrar notificación
                showNotification('Mapping deleted successfully', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting mapping: ' + error.message, 'danger');
            });
    });

    // API 

    // Función para borrar el mapeo
    async function deleteType(eventType) {
        const response = await fetch(`/api/event-types/${eventType}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Asegúrate de tener esta función
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete type');
        }
        
        return await response.json();
    }

});

