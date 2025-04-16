import { getCookie } from './utils.js'


document.addEventListener('DOMContentLoaded', function() {
    // Variables de estado
    let currentPage = 1;
    let perPage = 25;
    let totalItems = 0;
    let totalPages = 1;
    let currentData = [];

    // Elementos del DOM
    const tableBody = document.getElementById('data-table-body');
    const pagination = document.getElementById('pagination');
    const paginationInfo = document.getElementById('pagination-info');
    const perPageSelect = document.getElementById('per-page-select');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Inicializar
    fetchData();
    
    // Event listeners
    perPageSelect.addEventListener('change', function() {
        perPage = parseInt(this.value);
        currentPage = 1;
        fetchData();
    });

    searchBtn.addEventListener('click', function() {
        currentPage = 1;
        fetchData();
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            currentPage = 1;
            fetchData();
        }
    });

    // Función para obtener datos de la API
    function fetchData() {
        loadingSpinner.style.display = 'block';
        tableBody.innerHTML = '';
        
        const searchTerm = searchInput.value.trim();
        
        const url = `/api/ingestion-events?page=${currentPage}&per_page=${perPage}${
            searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''
        }`;

        fetch(url, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                currentData = data.data;
                totalItems = data.pagination.total;
                totalPages = data.pagination.total_pages;
                
                renderTable();
                renderPagination();
                updatePaginationInfo();
                
                loadingSpinner.style.display = 'none';
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                loadingSpinner.style.display = 'none';
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading data: ${error.message}</td></tr>`;
            });
    }

    // Función para renderizar la tabla
    function renderTable() {
        tableBody.innerHTML = '';
        
        if (currentData.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center">No data found</td></tr>`;
            return;
        }
        
        currentData.forEach(item => {
            const row = document.createElement('tr');
            
            // Formatear timestamp para mejor legibilidad
            const timestamp = new Date(item.timestamp_creacion);
            const formattedTimestamp = timestamp.toLocaleString();
            
            row.innerHTML = `
                <td>${item.uuid_evento_origen}</td>
                <td>${item.source_table}</td>
                <td>${item.evento_origen_mensaje || '-'}</td>
                <td>${formattedTimestamp}</td>
                <td class="actions-column">
                    <a href="/history/${item.uuid_evento_origen}" class="btn btn-sm btn-outline-primary me-1">
                        <i class="bi bi-eye"></i>
                    </a>
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    // Función para renderizar la paginación
    function renderPagination() {
        pagination.innerHTML = '';
        
        // Botón Anterior
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" aria-label="Previous">&laquo;</a>`;
        prevLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                fetchData();
            }
        });
        pagination.appendChild(prevLi);
        
        // Páginas
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        if (startPage > 1) {
            const firstLi = document.createElement('li');
            firstLi.className = 'page-item';
            firstLi.innerHTML = `<a class="page-link" href="#">1</a>`;
            firstLi.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = 1;
                fetchData();
            });
            pagination.appendChild(firstLi);
            
            if (startPage > 2) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                pagination.appendChild(ellipsisLi);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            pageLi.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                fetchData();
            });
            pagination.appendChild(pageLi);
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item disabled';
                ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                pagination.appendChild(ellipsisLi);
            }
            
            const lastLi = document.createElement('li');
            lastLi.className = 'page-item';
            lastLi.innerHTML = `<a class="page-link" href="#">${totalPages}</a>`;
            lastLi.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = totalPages;
                fetchData();
            });
            pagination.appendChild(lastLi);
        }
        
        // Botón Siguiente
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" aria-label="Next">&raquo;</a>`;
        nextLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                fetchData();
            }
        });
        pagination.appendChild(nextLi);
    }

    // Función para actualizar la información de paginación
    function updatePaginationInfo() {
        const start = (currentPage - 1) * perPage + 1;
        const end = Math.min(currentPage * perPage, totalItems);
        
        paginationInfo.textContent = `Showing ${start} to ${end} of ${totalItems} entries`;
    }
});
