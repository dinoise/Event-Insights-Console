import { getCookie, showNotification } from './utils.js'

document.addEventListener('DOMContentLoaded', function() {
    // Configuración de la edición en línea
    const editables = document.querySelectorAll('.editable-container');
    
    editables.forEach(container => {
        const content = container.querySelector('.editable-content');
        const editBtn = container.querySelector('.begin-edit');
        const controls = container.querySelector('.editable-controls');
        const confirmBtn = container.querySelector('.confirm-edit');
        const cancelBtn = container.querySelector('.cancel-edit');

        let originalValue = content.textContent.trim();
        
        const isTextMuted = container.querySelector('.text-muted') !== null;

        // Iniciar edición al hacer clic en el botón Editar
        editBtn.addEventListener('click', () => {
            const currentValue = originalValue;
            
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'editable-input form-control form-control-sm';
            input.value = isTextMuted ? '' : currentValue;
            
            content.innerHTML = '';
            content.appendChild(input);
            content.classList.add('editing');
            
            // Mostrar controles y ocultar botón de edición
            controls.classList.add('show');
            editBtn.classList.add('d-none');
            
            input.focus();
            
            // Manejar teclado
            input.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') confirmEdit();
                if (e.key === 'Escape') cancelEdit();
            });
        });

        // Buttons
        confirmBtn.addEventListener('click', confirmEdit);
        cancelBtn.addEventListener('click', cancelEdit);

        // Functions
        async function confirmEdit() {
            const input = content.querySelector('input');
            const newValue = input.value.trim();
            const field = container.dataset.field;

            // Validar campo vacío
            if (!newValue) {         
                showNotification('El valor no puede estar vacío', 'danger');
                cancelEdit();
                return;
            }

            content.textContent = newValue;
            
            if (isTextMuted) {
                content.classList.remove('text-muted');
                content.classList.remove('font-italic');
            }
            content.classList.remove('editing');
            controls.classList.remove('show');
            editBtn.classList.remove('d-none');

            // Llamar al servicio para actualizar
            updateType(field, newValue);
        }

        function cancelEdit() {
            content.textContent = originalValue;
            
            content.classList.remove('editing');
            controls.classList.remove('show');
            editBtn.classList.remove('d-none');
        }
    });

    // Función para actualizar el mapeo
    function updateType(field, value) {
        const typeId = window.location.pathname.split('/').pop();

        // Mapear los nombres de campo internos a los que espera la API
        const fieldMapping = {
            'field_name': 'event_type_name',
            'field_description': 'event_type_description',
            'field_action': 'event_type_action',
            'field_story_message': 'event_type_story_message',
            'field_pubsub': 'event_type_pubsub_topic_name',
            'field_documentation': 'event_documentation_link'
        };
        
        // Crear el payload con el nombre correcto del campo
        const apiField = fieldMapping[field];
        if (!apiField) {
            console.error('Field not found:', field);
            return;
        }
        
        const payload = {
            [apiField]: value
        };
        
        fetch(`/api/event-types/${typeId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify(payload)
        })
        .then(async response => {
            if (response.ok) {
                return response.json();
            }

            let errorMessage = `Error ${response.status}: ${response.statusText}`;
            const errorJson = await response.json();
            
            console.error(errorJson.errors);
            throw new Error(errorMessage);
        })
        .then(data => {
            // Mostrar notificación de éxito
            showNotification('Cambios guardados exitosamente', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            // Mostrar notificación de error
            showNotification(error.message || 'Error al guardar cambios', 'danger');
            
            // Revertir visualmente el cambio
            const container = document.querySelector(`.editable-container[data-field="${field}"]`);
            const content = container.querySelector('.editable-content');

            content.textContent = originalValue;
        });
    }
        
});

