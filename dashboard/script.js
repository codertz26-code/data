// Inapakia data kutoka server kila sekunde 30
function loadData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            updateTable(data);
            updateStats(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateTable(data) {
    const tbody = document.querySelector('#dataTable tbody');
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(row.timestamp).toLocaleString()}</td>
            <td>${row.network}</td>
            <td>${row.data}</td>
            <td>${row.signal}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateStats(data) {
    // Jumla ya data
    const total = data.reduce((sum, row) => sum + row.data, 0);
    document.getElementById('totalData').textContent = total.toFixed(2) + ' MB';
    
    // Mtandao wa sasa (wa kwanza kwenye list)
    if (data.length > 0) {
        document.getElementById('currentNetwork').textContent = data[0].network;
    }
    
    // Data za leo
    const today = new Date().toDateString();
    const todayData = data
        .filter(row => new Date(row.timestamp).toDateString() === today)
        .reduce((sum, row) => sum + row.data, 0);
    document.getElementById('todayData').textContent = todayData.toFixed(2) + ' MB';
}

// Pakia data mara ya kwanza
loadData();

// Endelea kupakia kila sekunde 30
setInterval(loadData, 30000);
