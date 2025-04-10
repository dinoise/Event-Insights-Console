import { getCookie, showNotification } from './utils.js'

document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.getElementById('create-source-btn');
    const createModal = new bootstrap.Modal('#createEventSourceModal');
    const confirmCreateBtn = document.getElementById('confirm-create-event-source');
    const eventSourceForm = document.getElementById('source-form');

    const deleteModal = new bootstrap.Modal('#deleteSourceModal');
    const deleteBtn = document.querySelectorAll('.delete-source');
    const confirmDeleteBtn = document.getElementById('confirm-delete-source')

    let currentSource = null;
    
    // Botones

    createBtn.addEventListener('click', function() {
        createModal.show();
    });

    // Crear nuevo event source
    confirmCreateBtn.addEventListener('click', async function() {
        if (!eventSourceForm.checkValidity()) {
            eventSourceForm.classList.add('was-validated');
            return;
        }
        
        const payload = {
            source_name: document.getElementById('source-name').value,
            source_description: document.getElementById('source-description').value
        };
        
        try {
            confirmCreateBtn.disabled = true;
            confirmCreateBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';
            
            postSource(payload)
                .then(response => {
                    showNotification('Event source created successfully!', 'success');
                    createModal.hide();

                    const data = response.data.new_source
                    
                    // Redirigir al nuevo event source o recargar la página
                    window.location.href = `/sources/${data.source_id}`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error deleting mapping: ' + error.message, 'danger');
                });
            
        } catch (error) {
            console.error('Error creating event source:', error);
            showNotification('Error: ' + error.message, 'danger');
        } finally {
            confirmCreateBtn.disabled = false;
            confirmCreateBtn.textContent = 'Create';
        }
    });

    deleteBtn.forEach(btn => {
        btn.addEventListener('click', function() {
            currentSource = this.dataset.sourceId;
            console.log(currentSource)
            deleteModal.show();
        });
    });

    confirmDeleteBtn.addEventListener('click', function() {
        if (!currentSource) {
            return
        }

        deleteSource(currentSource)
            .then(() => {
                deleteModal.hide();
                // Eliminar la fila de la tabla
                document.querySelector(`tr[data-source-id="${currentSource}"]`).remove();
                // Mostrar notificación
                showNotification('Mapping deleted successfully', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting mapping: ' + error.message, 'danger');
            });
    });

    // API 

    async function postSource(payload) {
        const response = await fetch('/api/sources', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create event source');
        }
        
        return await response.json();
    }

    // Función para borrar el mapeo
    async function deleteSource(eventSource) {
        const response = await fetch(`/api/sources/${eventSource}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Asegúrate de tener esta función
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete source');
        }
        
        return await response.json();
    }

});

