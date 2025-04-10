import { getCookie, showNotification, validateBQ } from './utils.js'

document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.getElementById('create-type-btn');
    const createModal = new bootstrap.Modal('#createEventTypeModal');
    const confirmCreateBtn = document.getElementById('confirm-create-event-type');
    const eventTypeForm = document.getElementById('event-type-form');
    const versionInput = document.getElementById('event-version');
    const versionSuggestBtn = document.getElementById('version-suggest-btn');

    const deleteModal = new bootstrap.Modal('#deleteTypeModal');
    const deleteBtn = document.querySelectorAll('.delete-type');
    const confirmDeleteBtn = document.getElementById('confirm-delete-type')

    let currentType = null;
    
    // Botones

    createBtn.addEventListener('click', function() {
        createModal.show();
    });

    // Botón para sugerir versión
    versionSuggestBtn.addEventListener('click', function() {
        const currentVersion = versionInput.value;
        versionInput.value = suggestNextVersion(currentVersion);
    });

    // Crear nuevo event type
    confirmCreateBtn.addEventListener('click', async function() {
        if (!eventTypeForm.checkValidity()) {
            eventTypeForm.classList.add('was-validated');
            return;
        }
        
        const payload = {
            event_type_name: document.getElementById('event-type-name').value,
            event_type_description: document.getElementById('event-description').value,
            event_type_action: document.getElementById('event-type-action').value,
            event_domain: document.getElementById('event-domain').value,
            event_stage: document.getElementById('event-stage').value,
            event_type_story_message: document.getElementById('event-story-message').value,
            event_type_version: document.getElementById('event-version').value,
            event_documentation_link: document.getElementById('event-doc-link').value || null,
            event_type_pubsub_topic_name: document.getElementById('event-pubsub').value
        };
        
        try {
            confirmCreateBtn.disabled = true;
            confirmCreateBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';
            
            postType(payload)
                .then(response => {
                    showNotification('Event type created successfully!', 'success');
                    createModal.hide();
                    
                    const data = response.data.new_event_type

                    // Redirigir al nuevo event type o recargar la página
                    window.location.href = `/event-types/${data.event_type_id}`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error deleting mapping: ' + error.message, 'danger');
                });
            
        } catch (error) {
            console.error('Error creating event type:', error);
            showNotification('Error: ' + error.message, 'danger');
        } finally {
            confirmCreateBtn.disabled = false;
            confirmCreateBtn.textContent = 'Create';
        }
    });

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

    // Inputs

    // Validación del formato de versión
    versionInput.addEventListener('focusout', function() {
        const versionRegex = /^\d+\.\d+$/;
        if (!versionRegex.test(versionInput.value)) {
            alert('Version format should be MAJOR.MINOR (e.g. 1.0)');
            versionInput.value = '1.0';
        }
    });

    // Functions

    // Función para sugerir versión
    function suggestNextVersion(currentVersion) {
        if (!currentVersion) return '1.0';
        
        try {
            const versionParts = currentVersion.split('.');
            if (versionParts.length === 2) {
                const major = parseInt(versionParts[0]);
                const minor = parseInt(versionParts[1]);
                if (!isNaN(major) && !isNaN(minor)) {
                    return `${major}.${minor + 1}`;
                }
            }
        } catch (e) {
            console.error('Error parsing version:', e);
        }
        
        return '1.0';
    }

    // API 

    async function postType(payload) {
        const response = await fetch('/api/event-types', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create event type');
        }
        
        return await response.json();
    }

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

