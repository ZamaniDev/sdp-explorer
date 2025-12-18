// ============================================
// GLOBAL STATE
// ============================================
const endpoints = JSON.parse(document.getElementById('endpoints-data').textContent);
let currentInputMode = 'form';
let currentViewMode = 'smart';
let currentQuickViewMode = 'smart';
let lastResponse = null;
let lastResponseData = null;
let currentPage = 1;
let rowsPerPage = 20;
let allRenderedItems = [];
let searchFilterCount = 0;
let discoveredFields = new Set();

// ============================================
// TAB MANAGEMENT
// ============================================
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// ============================================
// ENDPOINT MANAGEMENT
// ============================================
function updateEndpoints() {
    const category = document.getElementById('category').value;
    const endpointSelect = document.getElementById('endpoint');
    const placeholdersContainer = document.getElementById('placeholders-container');
    
    endpointSelect.innerHTML = '<option value="">-- Select Endpoint --</option>';
    placeholdersContainer.innerHTML = '';
    
    if (category && endpoints[category]) {
        Object.entries(endpoints[category]).forEach(([name, path]) => {
            const option = document.createElement('option');
            option.value = path;
            option.textContent = `${name} (${path})`;
            endpointSelect.appendChild(option);
        });
    }
}

function updateInputMode() {
    const path = document.getElementById('endpoint').value;
    const placeholdersContainer = document.getElementById('placeholders-container');
    placeholdersContainer.innerHTML = '';
    
    const matches = path.match(/\{([^}]+)\}/g);
    if (matches) {
        matches.forEach(match => {
            const key = match.replace(/[{}]/g, '');
            const div = document.createElement('div');
            div.className = 'form-group';
            div.innerHTML = `
                <label>${key}:</label>
                <input type="text" id="placeholder-${key}" placeholder="Enter ${key}">
            `;
            placeholdersContainer.appendChild(div);
        });
    }
}

// ============================================
// INPUT MODE MANAGEMENT
// ============================================
function setInputMode(mode) {
    currentInputMode = mode;
    document.getElementById('mode-form').classList.toggle('active', mode === 'form');
    document.getElementById('mode-json').classList.toggle('active', mode === 'json');
    document.getElementById('input-form-mode').style.display = mode === 'form' ? 'block' : 'none';
    document.getElementById('input-json-mode').style.display = mode === 'json' ? 'block' : 'none';
}

function setViewMode(mode) {
    currentViewMode = mode;
    document.getElementById('view-smart').classList.toggle('active', mode === 'smart');
    document.getElementById('view-json').classList.toggle('active', mode === 'json');
    document.getElementById('response-smart-view').style.display = mode === 'smart' ? 'block' : 'none';
    document.getElementById('response-json-view').style.display = mode === 'json' ? 'block' : 'none';
    document.getElementById('result-search').style.display = mode === 'smart' ? 'block' : 'none';
}

function setQuickViewMode(mode) {
    currentQuickViewMode = mode;
    document.getElementById('quick-view-smart').classList.toggle('active', mode === 'smart');
    document.getElementById('quick-view-json').classList.toggle('active', mode === 'json');
    
    if (lastResponse) {
        displayQuickResponse(lastResponse);
    }
}

// ============================================
// SEARCH FILTER MANAGEMENT
// ============================================
function addSearchFilter(fieldPath = '', fieldValue = '') {
    searchFilterCount++;
    const container = document.getElementById('search-filters-container');
    
    const filterDiv = document.createElement('div');
    filterDiv.className = 'search-filter-row';
    filterDiv.id = `search-filter-${searchFilterCount}`;
    filterDiv.innerHTML = `
        <div class="filter-inputs">
            <div style="flex: 1;">
                <input type="text" 
                       id="search-field-${searchFilterCount}" 
                       placeholder="Field path (e.g., status.name)"
                       class="search-field-input"
                       value="${fieldPath}">
            </div>
            <div style="flex: 1;">
                <input type="text" 
                       id="search-value-${searchFilterCount}" 
                       placeholder="Value to search for"
                       class="search-value-input"
                       value="${fieldValue}">
            </div>
            <button type="button" class="btn-remove" onclick="removeSearchFilter(${searchFilterCount})" title="Remove">
                ✕
            </button>
        </div>
    `;
    
    container.appendChild(filterDiv);
    
    if (fieldPath) {
        setTimeout(() => {
            const valueInput = document.getElementById(`search-value-${searchFilterCount}`);
            if (valueInput) valueInput.focus();
        }, 100);
    }
}

function removeSearchFilter(id) {
    const filterDiv = document.getElementById(`search-filter-${id}`);
    if (filterDiv) {
        filterDiv.remove();
    }
}

function buildInputDataFromForm() {
    const rowCount = parseInt(document.getElementById('form-row-count').value) || 20;
    const startIndex = parseInt(document.getElementById('form-start-index').value) || 1;
    const sortField = document.getElementById('form-sort-field').value;
    const sortOrder = document.getElementById('form-sort-order').value;
    const getTotal = document.getElementById('form-get-total').checked;
    
    rowsPerPage = rowCount;
    
    const inputData = {
        list_info: {
            row_count: rowCount,
            start_index: startIndex,
            get_total_count: getTotal
        }
    };
    
    if (sortField) {
        inputData.list_info.sort_field = sortField;
        inputData.list_info.sort_order = sortOrder;
    }
    
    const searchFields = {};
    const filterRows = document.querySelectorAll('.search-filter-row');
    
    filterRows.forEach(row => {
        const fieldInput = row.querySelector('.search-field-input');
        const valueInput = row.querySelector('.search-value-input');
        
        if (fieldInput && valueInput) {
            const field = fieldInput.value.trim();
            const value = valueInput.value.trim();
            
            if (field && value) {
                searchFields[field] = value;
            }
        }
    });
    
    if (Object.keys(searchFields).length > 0) {
        inputData.list_info.search_fields = searchFields;
    }
    
    return inputData;
}

// ============================================
// FIELD DISCOVERY
// ============================================
function discoverFilterableFields(data) {
    discoveredFields = new Set();
    
    let mainArray = null;
    const arrayKeys = ['requests', 'technicians', 'users', 'notes', 'worklogs', 'tasks', 'projects', 'reports'];
    
    for (const key of arrayKeys) {
        if (Array.isArray(data[key]) && data[key].length > 0) {
            mainArray = data[key];
            break;
        }
    }
    
    if (!mainArray) {
        for (const [key, value] of Object.entries(data)) {
            if (Array.isArray(value) && value.length > 0) {
                mainArray = value;
                break;
            }
        }
    }
    
    if (mainArray && mainArray.length > 0) {
        extractFieldPaths(mainArray[0], '');
        displayDiscoveredFields();
    }
}

function extractFieldPaths(obj, prefix) {
    if (!obj || typeof obj !== 'object') return;
    
    for (const [key, value] of Object.entries(obj)) {
        const currentPath = prefix ? `${prefix}.${key}` : key;
        
        if (value === null || value === undefined) {
            discoveredFields.add(currentPath);
        } else if (Array.isArray(value)) {
            discoveredFields.add(currentPath);
        } else if (typeof value === 'object') {
            const keys = Object.keys(value);
            
            if (keys.includes('name') || keys.includes('id') || keys.includes('value')) {
                if (value.name !== undefined) discoveredFields.add(`${currentPath}.name`);
                if (value.id !== undefined) discoveredFields.add(`${currentPath}.id`);
                if (value.value !== undefined) discoveredFields.add(`${currentPath}.value`);
                if (value.display_value !== undefined) discoveredFields.add(`${currentPath}.display_value`);
            }
            
            if (prefix.split('.').length < 2) {
                extractFieldPaths(value, currentPath);
            }
        } else {
            discoveredFields.add(currentPath);
        }
    }
}

function displayDiscoveredFields() {
    const container = document.getElementById('discovered-fields');
    const chipsContainer = document.getElementById('discovered-fields-chips');
    const countSpan = document.getElementById('discovered-count');
    const noResponseHint = document.getElementById('no-response-hint');
    
    if (discoveredFields.size === 0) {
        container.style.display = 'none';
        noResponseHint.style.display = 'block';
        return;
    }
    
    container.style.display = 'block';
    noResponseHint.style.display = 'none';
    countSpan.textContent = `${discoveredFields.size} fields found`;
    
    chipsContainer.innerHTML = '';
    
    const sortedFields = Array.from(discoveredFields).sort();
    
    const grouped = {};
    sortedFields.forEach(field => {
        const parts = field.split('.');
        const group = parts[0];
        if (!grouped[group]) grouped[group] = [];
        grouped[group].push(field);
    });
    
    Object.entries(grouped).forEach(([group, fields]) => {
        const groupLabel = document.createElement('div');
        groupLabel.className = 'field-group-label';
        groupLabel.textContent = group;
        chipsContainer.appendChild(groupLabel);
        
        fields.forEach(field => {
            const chip = document.createElement('button');
            chip.className = 'field-chip';
            chip.type = 'button';
            chip.textContent = field;
            chip.onclick = () => addSearchFilter(field);
            chipsContainer.appendChild(chip);
        });
    });
}

// ============================================
// API CALLS
// ============================================
async function testConnection() {
    const resultDiv = document.getElementById('connection-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = '<p>Testing connection...</p>';
    
    try {
        const response = await fetch('/api/test-connection', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            lastResponse = result;
            lastResponseData = result.data;
            
            discoverFilterableFields(result.data);
            
            resultDiv.innerHTML = `
                <p class="success">✅ Connection Successful!</p>
                <p>Status Code: <span class="status-badge status-200">${result.status_code}</span></p>
                ${renderSmartView(result.data)}
            `;
        } else {
            resultDiv.innerHTML = `
                <p class="error">❌ Connection Failed</p>
                <p>Error: ${result.error}</p>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
    }
}

async function executeApiCall() {
    const endpoint = document.getElementById('endpoint').value;
    const method = document.getElementById('method').value;
    const smartView = document.getElementById('response-smart-view');
    const jsonView = document.getElementById('response-json-view');
    const jsonContent = document.getElementById('response-json-content');
    
    if (!endpoint) {
        alert('Please select an endpoint');
        return;
    }
    
    const placeholders = {};
    const matches = endpoint.match(/\{([^}]+)\}/g);
    if (matches) {
        for (const match of matches) {
            const key = match.replace(/[{}]/g, '');
            const value = document.getElementById(`placeholder-${key}`).value;
            if (!value) {
                alert(`Please fill in ${key}`);
                return;
            }
            placeholders[key] = value;
        }
    }
    
    let inputData = {};
    if (currentInputMode === 'form') {
        inputData = buildInputDataFromForm();
        currentPage = inputData.list_info.start_index;
    } else {
        const inputDataText = document.getElementById('input-data').value;
        if (inputDataText.trim()) {
            try {
                inputData = JSON.parse(inputDataText);
            } catch (e) {
                alert('Invalid JSON in input data');
                return;
            }
        }
    }
    
    smartView.innerHTML = '<p>Executing...</p>';
    jsonContent.textContent = '';
    
    try {
        const response = await fetch('/api/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                method: method,
                endpoint: endpoint,
                input_data: inputData,
                placeholders: placeholders
            })
        });
        
        const result = await response.json();
        lastResponse = result;
        lastResponseData = result.data;
        
        if (result.success) {
            discoverFilterableFields(result.data);
            
            smartView.innerHTML = `
                <p class="success">✅ Success</p>
                <p>Status Code: <span class="status-badge status-200">${result.status_code}</span></p>
                ${renderSmartView(result.data)}
            `;
            
            jsonContent.textContent = JSON.stringify(result.data, null, 2);
            
            updatePaginationControls(result.data);
        } else {
            smartView.innerHTML = `
                <p class="error">❌ Failed</p>
                <p>Error: ${result.error}</p>
            `;
            jsonContent.textContent = result.error || 'Unknown error';
        }
    } catch (error) {
        smartView.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
        jsonContent.textContent = error.message;
    }
}

async function quickView(type) {
    const resultDiv = document.getElementById('quick-result');
    resultDiv.innerHTML = '<p>Loading...</p>';
    
    try {
        const response = await fetch(`/api/quick/${type}`);
        const result = await response.json();
        lastResponse = result;
        
        displayQuickResponse(result);
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
    }
}

function displayQuickResponse(result) {
    const resultDiv = document.getElementById('quick-result');
    
    if (result.success) {
        if (currentQuickViewMode === 'smart') {
            resultDiv.innerHTML = `
                <p class="success">✅ Success</p>
                ${renderSmartView(result.data)}
            `;
        } else {
            resultDiv.innerHTML = `
                <p class="success">✅ Success</p>
                <pre>${JSON.stringify(result.data, null, 2)}</pre>
            `;
        }
    } else {
        resultDiv.innerHTML = `<p class="error">❌ Error: ${result.error}</p>`;
    }
}

// ============================================
// SMART JSON RENDERER
// ============================================
function renderSmartView(data) {
    allRenderedItems = [];
    
    if (!data || typeof data !== 'object') {
        return `<p>${String(data)}</p>`;
    }
    
    let mainArray = null;
    let listInfo = null;
    let arrayKey = null;
    
    const arrayKeys = ['requests', 'technicians', 'users', 'notes', 'worklogs', 'tasks', 'projects', 'reports'];
    for (const key of arrayKeys) {
        if (Array.isArray(data[key])) {
            mainArray = data[key];
            arrayKey = key;
            break;
        }
    }
    
    if (!mainArray) {
        for (const [key, value] of Object.entries(data)) {
            if (Array.isArray(value) && value.length > 0) {
                mainArray = value;
                arrayKey = key;
                break;
            }
        }
    }
    
    if (data.list_info) {
        listInfo = data.list_info;
    }
    
    if (mainArray && mainArray.length > 0) {
        return renderList(mainArray, listInfo, arrayKey);
    }
    
    if (!mainArray) {
        for (const [key, value] of Object.entries(data)) {
            if (typeof value === 'object' && value !== null && !Array.isArray(value) && Object.keys(value).length > 3) {
                return renderSingleObject(value, key);
            }
        }
    }
    
    return renderGenericStructure(data);
}

function renderList(items, listInfo, arrayKey) {
    allRenderedItems = items;
    
    let html = '';
    
    if (listInfo) {
        const totalCount = listInfo.total_count || '?';
        const showing = items.length;
        html += `
            <div class="info-banner">
                📊 ${arrayKey || 'Items'}: Showing ${showing} of ${totalCount}
                ${listInfo.has_more_rows ? ' • More results available' : ''}
            </div>
        `;
    }
    
    items.forEach((item, index) => {
        html += renderListItemCard(item, index);
    });
    
    return html || '<p>No items found</p>';
}

function renderListItemCard(item, index) {
    if (typeof item !== 'object' || item === null) {
        return `<div class="card"><div class="card-body">${String(item)}</div></div>`;
    }
    
    const preview = identifyPreviewFields(item);
    const identifier = preview.id || `Item ${index + 1}`;
    
    return `
        <div class="card card-clickable" onclick="showDetailModal(${index})" data-index="${index}">
            <div class="card-header">
                <strong>${identifier}</strong>
                ${preview.badges}
            </div>
            <div class="card-body">
                <div class="card-preview">
                    ${preview.html}
                </div>
                <div class="card-footer">
                    <small>Click for full details →</small>
                </div>
            </div>
        </div>
    `;
}

function identifyPreviewFields(obj) {
    let id = '';
    let badges = '';
    let previewFields = [];
    
    const idFields = ['id', 'request_id', 'ticket_id', 'user_id', 'technician_id'];
    const nameFields = ['name', 'subject', 'title', 'description', 'short_description'];
    const statusFields = ['status', 'priority', 'state'];
    const timestampFields = ['created_time', 'updated_time', 'due_by_time'];
    const personFields = ['requester', 'technician', 'created_by', 'assigned_to'];
    
    for (const field of idFields) {
        if (obj[field]) {
            id = `#${obj[field]}`;
            break;
        }
    }
    
    for (const field of statusFields) {
        if (obj[field] && typeof obj[field] === 'object') {
            const name = obj[field].name || obj[field].value;
            const color = obj[field].color || '#999';
            if (name) {
                badges += `<span class="badge" style="background: ${color}">${name}</span>`;
            }
        }
    }
    
    const allFields = Object.keys(obj);
    
    for (const field of nameFields) {
        if (obj[field] && previewFields.length < 3) {
            const value = typeof obj[field] === 'object' ? obj[field].name || JSON.stringify(obj[field]) : obj[field];
            if (value && String(value).trim()) {
                previewFields.push({key: field, value: truncate(String(value), 100)});
            }
        }
    }
    
    for (const field of personFields) {
        if (obj[field] && previewFields.length < 4) {
            const person = obj[field];
            const personName = typeof person === 'object' ? person.name : person;
            if (personName) {
                previewFields.push({key: field, value: personName});
            }
        }
    }
    
    for (const field of timestampFields) {
        if (obj[field] && previewFields.length < 5) {
            const time = typeof obj[field] === 'object' ? obj[field].display_value || obj[field].value : obj[field];
            if (time) {
                previewFields.push({key: field, value: time});
            }
        }
    }
    
    if (previewFields.length < 5) {
        for (const [key, value] of Object.entries(obj)) {
            if (previewFields.length >= 5) break;
            if (!previewFields.find(f => f.key === key) && 
                !idFields.includes(key) && 
                !statusFields.includes(key) &&
                value !== null &&
                typeof value !== 'object') {
                previewFields.push({key, value: truncate(String(value), 80)});
            }
        }
    }
    
    let html = '<div class="preview-grid">';
    previewFields.forEach(field => {
        html += `
            <div class="preview-field">
                <span class="field-label">${formatFieldName(field.key)}:</span>
                <span class="field-value">${field.value}</span>
            </div>
        `;
    });
    html += '</div>';
    
    return { id, badges, html };
}

function renderSingleObject(obj, title) {
    return `
        <div class="single-object">
            <h3>${title || 'Object'}</h3>
            ${renderObjectDetails(obj)}
        </div>
    `;
}

function renderObjectDetails(obj, level = 0) {
    if (typeof obj !== 'object' || obj === null) {
        return `<span>${String(obj)}</span>`;
    }
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return '<em>Empty array</em>';
        return `
            <div class="array-container">
                ${obj.map((item, i) => `
                    <details>
                        <summary>Item ${i + 1}</summary>
                        ${renderObjectDetails(item, level + 1)}
                    </details>
                `).join('')}
            </div>
        `;
    }
    
    let html = '<div class="object-details">';
    
    for (const [key, value] of Object.entries(obj)) {
        const fieldName = formatFieldName(key);
        
        if (value === null || value === undefined) {
            html += `
                <div class="detail-row">
                    <span class="detail-label">${fieldName}:</span>
                    <span class="detail-value null">N/A</span>
                </div>
            `;
        } else if (typeof value === 'object') {
            if (Array.isArray(value)) {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">${fieldName}:</span>
                        <details class="nested-details">
                            <summary>${value.length} items</summary>
                            ${renderObjectDetails(value, level + 1)}
                        </details>
                    </div>
                `;
            } else {
                html += `
                    <div class="detail-row">
                        <span class="detail-label">${fieldName}:</span>
                        <details class="nested-details">
                            <summary>View details</summary>
                            ${renderObjectDetails(value, level + 1)}
                        </details>
                    </div>
                `;
            }
        } else {
            let displayValue = String(value);
            
            if (key.includes('color') && value.startsWith('#')) {
                displayValue = `<span class="badge" style="background: ${value}">${value}</span>`;
            } else if (key.includes('time') || key.includes('date')) {
                displayValue = `<span class="timestamp">${value}</span>`;
            } else if (typeof value === 'boolean') {
                displayValue = value ? '✓ Yes' : '✗ No';
            } else if (displayValue.length > 200) {
                displayValue = `<div class="long-text">${displayValue}</div>`;
            }
            
            html += `
                <div class="detail-row">
                    <span class="detail-label">${fieldName}:</span>
                    <span class="detail-value">${displayValue}</span>
                </div>
            `;
        }
    }
    
    html += '</div>';
    return html;
}

function renderGenericStructure(data) {
    let html = '<div class="generic-structure">';
    
    for (const [key, value] of Object.entries(data)) {
        html += `
            <details open>
                <summary><strong>${formatFieldName(key)}</strong></summary>
                ${renderObjectDetails(value)}
            </details>
        `;
    }
    
    html += '</div>';
    return html;
}

// ============================================
// MODAL MANAGEMENT
// ============================================
function showDetailModal(index) {
    const item = allRenderedItems[index];
    if (!item) return;
    
    const modal = document.getElementById('detail-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');
    
    const itemId = item.id || item.name || item.subject || `Item ${index + 1}`;
    title.textContent = `Details: ${itemId}`;
    
    body.innerHTML = renderObjectDetails(item);
    
    modal.style.display = 'flex';
}

function closeModal(event) {
    const modal = document.getElementById('detail-modal');
    modal.style.display = 'none';
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function formatFieldName(key) {
    return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

function filterResults(searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    const cards = document.querySelectorAll('#response-smart-view .card-clickable');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

function filterQuickResults(searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    const cards = document.querySelectorAll('#quick-result .card-clickable');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

// ============================================
// PAGINATION
// ============================================
function updatePaginationControls(data) {
    const controls = document.getElementById('pagination-controls');
    const listInfo = data.list_info;
    
    if (!listInfo || !listInfo.total_count) {
        controls.style.display = 'none';
        return;
    }
    
    const totalCount = parseInt(listInfo.total_count);
    
    controls.style.display = 'block';
    document.getElementById('pagination-info').textContent = 
        `Showing ${currentPage} - ${Math.min(currentPage + rowsPerPage - 1, totalCount)} of ${totalCount}`;
    
    document.getElementById('btn-prev').disabled = currentPage <= 1;
    document.getElementById('btn-next').disabled = !listInfo.has_more_rows;
}

function previousPage() {
    if (currentPage > rowsPerPage) {
        currentPage -= rowsPerPage;
    } else {
        currentPage = 1;
    }
    document.getElementById('form-start-index').value = currentPage;
    executeApiCall();
}

function nextPage() {
    currentPage += rowsPerPage;
    document.getElementById('form-start-index').value = currentPage;
    executeApiCall();
}

// ============================================
// HISTORY MANAGEMENT
// ============================================
async function loadHistory() {
    const historyDiv = document.getElementById('history-list');
    historyDiv.innerHTML = '<p>Loading...</p>';
    
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        
        if (history.length === 0) {
            historyDiv.innerHTML = '<p>No requests yet</p>';
            return;
        }
        
        let html = '';
        history.reverse().forEach(entry => {
            const statusClass = entry.status_code === 200 ? 'status-200' : 'status-error';
            html += `
                <div class="card">
                    <div class="card-header">
                        <strong>${entry.method}</strong> ${entry.timestamp}
                        <span class="status-badge ${statusClass}">${entry.status_code || 'Error'}</span>
                    </div>
                    <div class="card-body">
                        <p><strong>URL:</strong> ${entry.url}</p>
                        ${entry.error ? `<p class="error">Error: ${entry.error}</p>` : ''}
                        <details>
                            <summary>View Full Details</summary>
                            <pre>${JSON.stringify(entry, null, 2)}</pre>
                        </details>
                    </div>
                </div>
            `;
        });
        historyDiv.innerHTML = html;
    } catch (error) {
        historyDiv.innerHTML = `<p class="error">Error loading history: ${error.message}</p>`;
    }
}