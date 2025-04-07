import { getCookie, showNotification } from './utils.js'

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
    
});

// Manejar cambios en el tipo de evento
document.querySelector('.event-type-select').addEventListener('change', function() {
    const newEventTypeId = this.value;
    const currentValue = this.dataset.current;
    
    if (newEventTypeId !== currentValue) {
        updateMappingRelation('event_type_id', newEventTypeId, this);
    }
});

// Manejar cambios en la fuente
document.querySelector('.source-select').addEventListener('change', function() {
    const newSourceId = this.value;
    const currentValue = this.dataset.current;
    
    if (newSourceId !== currentValue) {
        updateMappingRelation('source_id', newSourceId, this);
    }
});

// Función para actualizar la relación
function updateMappingRelation(field, value, selectElement) {
    const mappingId = window.location.pathname.split('/').pop();
    const payload = {
        [field]: parseInt( value )
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
        const data = await response.json(); 

        if (!response.ok) {
            // Extraer el mensaje de error de la respuesta
            const errorMsg = data.errors ||
                            data.message || 
                            `Error ${response.status}: ${response.statusText}`;
            throw new Error(errorMsg);
        }
        return data;
    })
    .then(data => {
        // Actualizar el valor actual en el dropdown
        selectElement.dataset.current = value;
        showNotification('Relación actualizada exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        // Revertir al valor anterior
        selectElement.value = selectElement.dataset.current;
        showNotification('Error al actualizar relación: ' + error.message, 'danger');
    });
}