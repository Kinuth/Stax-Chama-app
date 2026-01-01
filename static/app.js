const API_BASE = window.location.origin + '/api';

// 1. Handle Login
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch(`${API_BASE}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        showDashboard();
    } else {
        alert("Login Failed. Check credentials.");
    }
}

// 2. Fetch and Display Groups
async function loadGroups() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/groups/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
        const groups = await response.json();
        const container = document.getElementById('group-list');
        container.innerHTML = groups.map(g => `
            <div class="col-md-4">
                <div class="card mb-3 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${g.name}</h5>
                        <p class="card-text text-success">Balance: KES ${g.balance}</p>
                        <button class="btn btn-sm btn-primary">Apply Loan</button>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

function showDashboard() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    loadGroups();
}

function logout() {
    localStorage.clear();
    location.reload();
}

// Auto-login if token exists
if (localStorage.getItem('access_token')) {
    showDashboard();
}