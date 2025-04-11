import { getCookie, showNotification, validateBQ } from './utils.js'

document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = new bootstrap.Modal('#deleteMappingModal');

    const createBtn = document.getElementById('create-mapping-btn');
    const createModal = new bootstrap.Modal('#createMappingModal');
    const confirmCreateBtn = document.getElementById('confirm-create-mapping');
    const mappingForm = document.getElementById('mapping-form');

    const inputTargetDataset = document.getElementById('target-dataset');
    const inputTargetTable = document.getElementById('target-table');

    const datasetIndicator = document.getElementById('dataset-indicator');
    const tableIndicator = document.getElementById('table-indicator');

    const versionInput = document.getElementById('mapping-version');
    const versionSuggestBtn = document.getElementById('version-suggest-btn');
    
    let datasetIsValid = false;
    let tableIsValid = false;
    let versionIsValid = true

    let currentDataset = ''; // Para mantener el estado del dataset válido

    let currentMappingId = null;

    // Abrir modal al hacer clic en el botón
    createBtn.addEventListener('click', function() {
        createModal.show();
    });

    // Botón para sugerir versión
    versionSuggestBtn.addEventListener('click', function() {
        const currentVersion = versionInput.value;
        versionInput.value = suggestNextVersion(currentVersion);
    });

    // Validación del formato de versión al salir del campo
    versionInput.addEventListener('focusout', function() {
        const versionRegex = /^\d+\.\d+$/;
        if (!versionRegex.test(versionInput.value)) {
            versionIsValid = false
            showNotification('Version format should be MAJOR.MINOR (e.g. 1.0)', 'warning');
            versionInput.value = '1.0';
        }
        versionIsValid = true
    });
    
    // Manejar la creación del mapeo
    confirmCreateBtn.addEventListener('click', async function() {
        if (!versionIsValid) {
            versionInput.classList.add('is-invalid');
            versionInput.focus()
            showNotification('Please validate the version', 'warning');
            return;
        }

        // Validar dataset primero
        if (!datasetIsValid) {
            showNotification('Please validate the dataset first', 'warning');
            return;
        }
        
        if (!tableIsValid) {
            showNotification(`Table in not valid`, 'danger');
            inputTargetTable.classList.add('is-invalid');
            return;
        }

        if (!mappingForm.checkValidity()) {
            mappingForm.classList.add('was-validated');
            return;
        }
        
        const payload = {
            event_mapping_description: document.getElementById('mapping-description').value,
            event_mapping_target_dataset: document.getElementById('target-dataset').value,
            event_mapping_target_table: document.getElementById('target-table').value,
            event_type_id: document.getElementById('event-type').value,
            source_id: document.getElementById('source').value,
            event_mapping_version: document.getElementById('mapping-version').value,
        };
        
        try {
            confirmCreateBtn.disabled = true;
            confirmCreateBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating...';
            
            const newMapping = await createMapping(payload);
            
            showNotification('Mapping created successfully!', 'success');
            createModal.hide();
            
            // Redirigir al nuevo mapeo o recargar la página
            window.location.href = `/event-mappings/${newMapping.event_mapping_id}`;
            
        } catch (error) {
            console.error('Error creating mapping:', error);
            showNotification('Error: ' + error.message, 'danger');
        } finally {
            confirmCreateBtn.disabled = false;
            confirmCreateBtn.textContent = 'Create';
        }
    });
    
    // Manejar clic en botones de borrado
    document.querySelectorAll('.delete-mapping').forEach(btn => {
        btn.addEventListener('click', function() {
            currentMappingId = this.dataset.mappingId;
            deleteModal.show();
        });
    });

    // Validación al salir del campo dataset
    inputTargetDataset.addEventListener("focusout", async (event) => {
        const newValue = inputTargetDataset.value.trim();
        
        if (!newValue) {
            datasetIsValid = false;
            showNotification('Dataset cannot be empty', 'danger');
            return;
        }

        // Mostrar estado de carga
        updateIndicator(datasetIndicator, 'loading');

        try {
            const isValid = await validateBQ({
                dataset: newValue,
                table: null
            });
            
            if (!isValid) {
                datasetIsValid = false;
                updateIndicator(datasetIndicator, 'invalid');
                showNotification(`Dataset is not valid`, 'danger');
                currentDataset = '';
                return
            } 

            datasetIsValid = true;
            updateIndicator(datasetIndicator, 'valid');
            showNotification('Dataset is valid', 'success');
            currentDataset = newValue;

            // Si ya hay un valor en tabla, validarla también
            if (inputTargetTable.value.trim()) {
                inputTargetTable.dispatchEvent(new Event('focusout'));
            }
            
        } catch (error) {
            datasetIsValid = false;
            updateIndicator(datasetIndicator, 'invalid');
            console.error('Validation error:', error);
            showNotification('Error during validation', 'danger');
        }
    });

    // Validación al salir del campo tabla (solo si hay dataset válido)
    inputTargetTable.addEventListener("focusout", async (event) => {
        const tableValue = inputTargetTable.value.trim();
        
        if (!tableValue){
            tableIsValid = false;
            showNotification('Please validate a dataset first', 'warning');
            return;
        } 
            
        
        if (!currentDataset) {
            tableIsValid = false;
            showNotification('Please validate a dataset first', 'warning');
            return;
        }
        
        // Mostrar estado de carga
        updateIndicator(tableIndicator, 'loading');

        try {
            const isValid = await validateBQ({
                dataset: currentDataset,
                table: tableValue
            });
            
            if (!isValid) {
                tableIsValid = false;
                updateIndicator(tableIndicator, 'invalid');
                showNotification(`Table is not valid`, 'danger');
                return
            }

            tableIsValid = true;
            updateIndicator(tableIndicator, 'valid');
            showNotification('Table is valid', 'success');
        
        } catch (error) {
            tableIsValid = false;
            console.error('Validation error:', error);
            updateIndicator(tableIndicator, 'invalid');
            showNotification('Error during table validation', 'danger');
        }
    });

    // Confirmar borrado
    document.getElementById('confirm-delete-mapping').addEventListener('click', function() {
        if (!currentMappingId) {
            return
        }

        deleteMapping(currentMappingId)
            .then(() => {
                deleteModal.hide();
                // Eliminar la fila de la tabla
                document.querySelector(`tr[data-mapping-id="${currentMappingId}"]`).remove();
                // Mostrar notificación
                showNotification('Mapping deleted successfully', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error deleting mapping: ' + error.message, 'danger');
            });
    });

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

    // Función para actualizar el indicador
    function updateIndicator(element, state) {
        // Limpiar contenido previo
        element.innerHTML = '';
        
        switch(state) {
            case 'loading':
                element.innerHTML = `
                    <span class="loading-indicator">
                        <i class="bi bi-arrow-repeat"></i>
                    </span>
                `;
                break;
            case 'valid':
                element.innerHTML = '<i class="bi bi-check-circle valid-indicator"></i>';
                break;
            case 'invalid':
                element.innerHTML = '<i class="bi bi-exclamation-circle invalid-indicator"></i>';
                break;
            default:
                element.innerHTML = '';
        }
    }
    
    // API

    // Función para crear el mapeo
    async function createMapping(payload) {
        const response = await fetch('/api/event-mapping', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create mapping');
        }
        
        const response_json = await response.json()

        return response_json.data;
    }

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
});
