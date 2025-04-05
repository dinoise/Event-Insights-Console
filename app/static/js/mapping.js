document.addEventListener('DOMContentLoaded', function() {
    // Configuración de la edición en línea
    const editables = document.querySelectorAll('.editable-container');
    let originalValue = '';
    
    editables.forEach(container => {
        const content = container.querySelector('.editable-content');
        const editBtn = container.querySelector('.begin-edit');
        const controls = container.querySelector('.editable-controls');
        const confirmBtn = container.querySelector('.confirm-edit');
        const cancelBtn = container.querySelector('.cancel-edit');
        
        // Iniciar edición al hacer clic en el botón Editar
        editBtn.addEventListener('click', () => {
            originalValue = content.textContent.trim();
            const isBadge = content.querySelector('span');
            const currentValue = isBadge ? isBadge.textContent.trim() : originalValue;
            
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'editable-input form-control form-control-sm';
            input.value = currentValue;
            
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
        
        function confirmEdit() {
            const input = content.querySelector('input');
            const newValue = input.value.trim();
            const field = container.dataset.field;
            
            // Actualizar visualmente
            if (content.querySelector('span')) {
                content.innerHTML = `<span class="badge bg-info">${newValue}</span>`;
            } else {
                content.textContent = newValue;
            }
            
            content.classList.remove('editing');
            controls.classList.remove('show');
            editBtn.classList.remove('d-none');
            
            // Llamar al servicio para actualizar
            updateMapping(field, newValue);
        }
        
        function cancelEdit() {
            if (content.querySelector('span')) {
                content.innerHTML = `<span class="badge bg-info">${originalValue}</span>`;
            } else {
                content.textContent = originalValue;
            }
            
            content.classList.remove('editing');
            controls.classList.remove('show');
            editBtn.classList.remove('d-none');
        }
        
        confirmBtn.addEventListener('click', confirmEdit);
        cancelBtn.addEventListener('click', cancelEdit);
    });
    
    // Función para actualizar el mapeo
    function updateMapping(field, value) {
        const mappingId = window.location.pathname.split('/').pop();
        
        // Mapear los nombres de campo internos a los que espera la API
        const fieldMapping = {
            'description': 'event_mapping_description',
            'target_dataset': 'event_mapping_target_dataset',
            'target_table': 'event_mapping_target_table'
        };
        
        // Crear el payload con el nombre correcto del campo
        const apiField = fieldMapping[field];
        if (!apiField) {
            console.error('Campo no reconocido:', field);
            return;
        }
        
        const payload = {
            [apiField]: value
        };
        
        fetch(`/api/event-mapping/${mappingId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify(payload)
        })
        .then(async response => {
            if (!response.ok) {
                let errorMessage = `Error ${response.status}: ${response.statusText}`;
                try {
                    const errorJson = await response.json();
                    if (errorJson.message) {
                        errorMessage = errorJson.message;
                    }
                } catch (e) {
                    console.error('Error al parsear respuesta de error:', e);
                }
                throw new Error(errorMessage);
            }
            return response.json();
        })
        .then(data => {
            console.log('Actualización exitosa:', data);
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
            if (content.querySelector('span')) {
                content.innerHTML = `<span class="badge bg-info">${originalValue}</span>`;
            } else {
                content.textContent = originalValue;
            }
        });
    }
    
    // Función auxiliar para mostrar notificaciones (opcional)
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
    
    // Función auxiliar para obtener cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});