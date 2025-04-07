document.addEventListener('DOMContentLoaded', function() {
    const columnsBody = document.getElementById('columns-body');
    const addColumnBtn = document.getElementById('add-column-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const deleteModal = new bootstrap.Modal('#confirmDeleteModal');
    
    let columnToDelete = null;
    const mappingId = window.location.pathname.split('/').pop();
    
    // Manejar borrado de columnas
    document.querySelectorAll('.delete-column').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            columnToDelete = row.dataset.columnId;
            deleteModal.show();
        });
    });
    
    confirmDeleteBtn.addEventListener('click', function() {
        if (columnToDelete) {
            deleteColumn(columnToDelete);
            deleteModal.hide();
        }
    });
    
    // Manejar edición de columnas
    document.querySelectorAll('.edit-column').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            enableEditMode(row);
        });
    });
    
    // Agregar nueva columna
    addColumnBtn.addEventListener('click', function() {
        const template = document.getElementById('new-column-template');
        const newRow = template.content.cloneNode(true);
        columnsBody.appendChild(newRow);
        
        // Configurar eventos para la nueva fila
        const addedRow = columnsBody.lastElementChild;
        addedRow.querySelector('.save-new-column').addEventListener('click', () => saveNewColumn(addedRow));
        addedRow.querySelector('.cancel-new-column').addEventListener('click', () => addedRow.remove());
    });
    
    function enableEditMode(row) {
        const cells = {
            sequence: row.querySelector('.sequence'),
            originColumn: row.querySelector('.origin-column'),
            targetColumn: row.querySelector('.target-column'),
            dataType: row.querySelector('.data-type'),
            nullable: row.querySelector('.nullable'),
            validationRegex: row.querySelector('.validation-regex'),
            actions: row.querySelector('td:last-child')
        };
        
        // Guardar valores originales
        const originalValues = {
            sequence: cells.sequence.textContent,
            originColumn: cells.originColumn.textContent,
            targetColumn: cells.targetColumn.textContent,
            dataType: cells.dataType.textContent,
            nullable: cells.nullable.querySelector('.badge').textContent === 'Yes',
            validationRegex: cells.validationRegex.textContent
        };
        
        // Crear inputs de edición
        cells.sequence.innerHTML = `<input type="number" class="form-control form-control-sm" 
            value="${originalValues.sequence}" min="1">`;
        
        cells.originColumn.innerHTML = `<input type="text" class="form-control form-control-sm" 
            value="${originalValues.originColumn}">`;
        
        cells.targetColumn.innerHTML = `<input type="text" class="form-control form-control-sm" 
            value="${originalValues.targetColumn}">`;
        
        cells.dataType.innerHTML = `
            <select class="form-select form-select-sm">
                <option value="STRING" ${originalValues.dataType === 'STRING' ? 'selected' : ''}>STRING</option>
                <option value="INT64" ${originalValues.dataType === 'INT64' ? 'selected' : ''}>INT64</option>
                <option value="FLOAT64" ${originalValues.dataType === 'FLOAT64' ? 'selected' : ''}>FLOAT64</option>
            </select>`;
        
        cells.nullable.innerHTML = `
            <select class="form-select form-select-sm">
                <option value="true" ${originalValues.nullable ? 'selected' : ''}>Yes</option>
                <option value="false" ${!originalValues.nullable ? 'selected' : ''}>No</option>
            </select>`;
        
        cells.validationRegex.innerHTML = `<input type="text" class="form-control form-control-sm" 
            value="${originalValues.validationRegex}">`;
        
        // Reemplazar botones con controles de edición
        cells.actions.innerHTML = `
            <button class="btn btn-sm btn-success save-edit me-1">
                <i class="bi bi-check"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger cancel-edit">
                <i class="bi bi-x"></i>
            </button>`;
        
        // Configurar eventos
        cells.actions.querySelector('.save-edit').addEventListener('click', () => {
            saveColumnEdit(row, originalValues);
        });
        
        cells.actions.querySelector('.cancel-edit').addEventListener('click', () => {
            cancelColumnEdit(row, originalValues);
        });
    }
    
    function saveColumnEdit(row, originalValues) {
        const inputs = {
            sequence: row.querySelector('.sequence input').value,
            originColumn: row.querySelector('.origin-column input').value,
            targetColumn: row.querySelector('.target-column input').value,
            dataType: row.querySelector('.data-type select').value,
            nullable: row.querySelector('.nullable select').value === 'true',
            validationRegex: row.querySelector('.validation-regex input').value
        };
        
        const columnId = row.dataset.columnId;
        const payload = {
            mapping_sequence: parseInt(inputs.sequence),
            mapping_origin_column: inputs.originColumn,
            mapping_target_column: inputs.targetColumn,
            mapping_data_type: inputs.dataType,
            mapping_nullable: inputs.nullable,
            mapping_validation_regex: inputs.validationRegex
        };
                
        updateColumn(columnId, payload, row);
    }
    
    function cancelColumnEdit(row, originalValues) {
        row.querySelector('.sequence').textContent = originalValues.sequence;
        row.querySelector('.origin-column').textContent = originalValues.originColumn;
        row.querySelector('.target-column').textContent = originalValues.targetColumn;
        row.querySelector('.data-type').textContent = originalValues.dataType;
        
        const nullableBadge = originalValues.nullable ? 
            '<span class="badge bg-success">Yes</span>' : 
            '<span class="badge bg-danger">No</span>';
        row.querySelector('.nullable').innerHTML = nullableBadge;
        
        row.querySelector('.validation-regex').textContent = originalValues.validationRegex;
        
        // Restaurar botones originales
        row.querySelector('td:last-child').innerHTML = `
            <button class="btn btn-sm btn-outline-primary edit-column me-1">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-column">
                <i class="bi bi-trash"></i>
            </button>`;
        
        // Reconfigurar eventos
        row.querySelector('.edit-column').addEventListener('click', () => enableEditMode(row));
        row.querySelector('.delete-column').addEventListener('click', function() {
            columnToDelete = row.dataset.columnId;
            deleteModal.show();
        });
    }
    
    function saveNewColumn(row) {
        const inputs = {
            sequence: row.querySelector('.sequence-input').value,
            originColumn: row.querySelector('.origin-column-input').value,
            targetColumn: row.querySelector('.target-column-input').value,
            dataType: row.querySelector('.data-type-select').value,
            nullable: row.querySelector('.nullable-select').value === 'true',
            validationRegex: row.querySelector('.validation-regex-input').value
        };
        
        const payload = {
            event_mapping_id: mappingId,
            mapping_sequence: inputs.sequence,
            mapping_origin_column: inputs.originColumn,
            mapping_target_column: inputs.targetColumn,
            mapping_data_type: inputs.dataType,
            mapping_nullable: inputs.nullable,
            mapping_validation_regex: inputs.validationRegex
        };
        
        createColumn(payload, row);
    }
    
    // Funciones de API
    function deleteColumn(columnId) {
        fetch(`/api/mapping-columns/${columnId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            }
        })
        .then(response => {
            if (response.ok) {
                document.querySelector(`tr[data-column-id="${columnId}"]`).remove();
                showNotification('Column deleted successfully', 'success');
            } else {
                throw new Error('Failed to delete column');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error deleting column', 'danger');
        });
    }
    
    function updateColumn(columnId, payload, row) {
        fetch(`/api/mapping-columns/${columnId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to update column');
        })
        .then(data => {
            // Actualizar la fila con los nuevos valores
            row.querySelector('.sequence').textContent = data.mapping_sequence;
            row.querySelector('.origin-column').textContent = data.mapping_origin_column;
            row.querySelector('.target-column').textContent = data.mapping_target_column;
            row.querySelector('.data-type').textContent = data.mapping_data_type;
            
            const nullableBadge = data.mapping_nullable ? 
                '<span class="badge bg-success">Yes</span>' : 
                '<span class="badge bg-danger">No</span>';
            row.querySelector('.nullable').innerHTML = nullableBadge;
            
            row.querySelector('.validation-regex').textContent = data.mapping_validation_regex || '';
            
            // Restaurar botones originales
            row.querySelector('td:last-child').innerHTML = `
                <button class="btn btn-sm btn-outline-primary edit-column me-1">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-column">
                    <i class="bi bi-trash"></i>
                </button>`;
            
            // Reconfigurar eventos
            row.querySelector('.edit-column').addEventListener('click', () => enableEditMode(row));
            row.querySelector('.delete-column').addEventListener('click', function() {
                columnToDelete = row.dataset.columnId;
                deleteModal.show();
            });
            
            showNotification('Column updated successfully', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating column', 'danger');
        });
    }
    
    function createColumn(payload, row) {
        fetch('/api/mapping-columns', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to create column');
        })
        .then(data => {
            // Crear nueva fila con los datos devueltos
            const newRow = document.createElement('tr');
            newRow.dataset.columnId = data.mapping_column_id;
            newRow.innerHTML = `
                <td class="sequence">${data.mapping_sequence}</td>
                <td class="origin-column">${data.mapping_origin_column}</td>
                <td class="target-column">${data.mapping_target_column}</td>
                <td class="data-type">${data.mapping_data_type}</td>
                <td class="nullable">
                    ${data.mapping_nullable ? 
                        '<span class="badge bg-success">Yes</span>' : 
                        '<span class="badge bg-danger">No</span>'}
                </td>
                <td class="validation-regex">${data.mapping_validation_regex || ''}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-column me-1">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-column">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>`;
            
            // Reemplazar la fila de edición
            row.replaceWith(newRow);
            
            // Configurar eventos
            newRow.querySelector('.edit-column').addEventListener('click', function() {
                enableEditMode(newRow);
            });
            
            newRow.querySelector('.delete-column').addEventListener('click', function() {
                columnToDelete = newRow.dataset.columnId;
                deleteModal.show();
            });
            
            showNotification('Column created successfully', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error creating column', 'danger');
        });
    }
    
    // Función auxiliar para obtener cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
        notification.style.zIndex = '1100';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
});