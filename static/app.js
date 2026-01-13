const API_BASE = window.location.origin + '/api';
let currentGroupId = null;
let actionModal;

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Bootstrap Modal
    const modalElement = document.getElementById('actionModal');
    if (modalElement) actionModal = new bootstrap.Modal(modalElement);

    // 2. Attach Listeners (using safe optional chaining ?)
    document.getElementById('tab-login')?.addEventListener('click', () => toggleAuth('login'));
    document.getElementById('tab-register')?.addEventListener('click', () => toggleAuth('register'));
    document.getElementById('logout-btn')?.addEventListener('click', logout);
    document.getElementById('btn-create-chama')?.addEventListener('click', handleCreateChama);
    document.getElementById('nav-dashboard')?.addEventListener('click', (e) => {
        e.preventDefault();
        showDashboard();
    });

    // 3. Attach listeners for login and register buttons
    document.getElementById('login-btn')?.addEventListener('click', login);
    document.getElementById('register-btn')?.addEventListener('click', register);

    // 4. Auto-load if logged in
    if (localStorage.getItem('access_token')) {
        showDashboard();
    }
});

// --- AUTH FUNCTIONS ---

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const res = await fetch(`${API_BASE}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('username', username);
        showDashboard();
    } else {
        let errorMsg;
        try {
            const errorData = await res.json();
            errorMsg = JSON.stringify(errorData);
        } catch (e) {
            // If response is not JSON (e.g. 500 HTML page), get text
            errorMsg = await res.text();
            // Optional: Truncate if too long (e.g. full HTML page)
            if (errorMsg.length > 200) errorMsg = errorMsg.substring(0, 200) + "...";
        }
        alert(`Login failed: ${res.status} ${res.statusText}\n${errorMsg}`);
    }
}

// Add this function to toggle between login and register forms
function toggleAuth(mode) {
    const loginTab = document.getElementById('tab-login');
    const registerTab = document.getElementById('tab-register');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (mode === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    }
}


// THIS WAS LIKELY MISSING OR MISSPELLED
async function register() {
    const payload = {
        username: document.getElementById('reg-username').value,
        password: document.getElementById('reg-password').value,
        phone_number: document.getElementById('reg-phone').value,
        national_id: document.getElementById('reg-id').value
    };

    const res = await fetch(`${API_BASE}/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        alert("Registration success! You can now login.");
        toggleAuth('login');
    } else {
        let errorMsg;
        try {
            const errorData = await res.json();
            errorMsg = JSON.stringify(errorData);
        } catch (e) {
            errorMsg = await res.text();
            if (errorMsg.length > 500) errorMsg = errorMsg.substring(0, 500) + "..."; // Longer limit for reg errors
        }
        alert(`Registration failed: ${res.status} ${res.statusText}\n${errorMsg}`);
    }
}

// --- CHAMA LOGIC ---

async function handleCreateChama() {
    const name = prompt("Enter Chama Name:");
    if (!name) return;

    const res = await fetch(`${API_BASE}/groups/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ name })
    });

    if (res.ok) {
        alert("Chama created!");
        loadSidebarChamas();
    }
}

async function loadGroupView(groupId) {
    currentGroupId = groupId;
    console.log("loadGroupView called with groupId:", groupId);  // Debug log
    const token = localStorage.getItem('access_token');

    document.getElementById('page-title').innerText = "Chama Management";

    const res = await fetch(`${API_BASE}/groups/${groupId}/summary/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
        const data = await res.json();
        const content = document.getElementById('dynamic-content');

        content.innerHTML = `
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="stat-card bg-primary text-white">
                        <h6>Total Group Balance</h6>
                        <h2 class="fw-bold">KES ${data.total_balance}</h2>
                        <button class="btn btn-light btn-sm mt-2 w-100" onclick="handleContribution()">
                            <i class="bi bi-plus-lg"></i> Add Contribution
                        </button>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="fw-bold mb-0">Members</h5>
                            <button class="btn btn-sm btn-banking" onclick="showInviteModal()">
                                <i class="bi bi-person-plus"></i> Invite Member
                            </button>
                        </div>
                        <ul class="list-group list-group-flush">
                            ${data.members.map(m => `
                                <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                                    <span><i class="bi bi-person-circle me-2 text-primary"></i>${m.username} ${!m.is_approved ? '(Pending Approval)' : ''}</span>
                        <span class="text-muted small">${m.phone_number || 'Member'}</span>
                                    <span class="text-muted small">${m.phone_number || 'Member'}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>

                <div class="col-12">
                    <div class="stat-card">
                        <h5 class="fw-bold mb-3">Recent Contributions</h5>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead class="table-light">
                                    <tr>
                                        <th>Member</th>
                                        <th>Amount</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody id="contribution-list">
                                    <tr><td colspan="3" class="text-center text-muted py-3">No recent contributions</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="col-12">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="fw-bold mb-0">Loan Requests</h5>
                            <button class="btn btn-sm btn-outline-primary" onclick="handleRequestLoan()">
                                <i class="bi bi-cash-stack"></i> Request Loan
                            </button>
                        </div>
                        <div class="table-responsive">
                            <table class="table align-middle">
                                <thead class="table-light">
                                    <tr>
                                        <th>Borrower</th>
                                        <th>Amount</th>
                                        <th>Total Due</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody id="loan-list-table">
                                    </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        // Fetch loans and refresh UI
        fetchGroupLoans(groupId);
        fetchGroupContributions(groupId);
    }
}

async function loadSidebarChamas() {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API_BASE}/groups/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
        const groups = await res.json();
        console.log("Groups Found Count:", groups.length);
        console.table(groups); // This will show your chamas in a nice table in the console

        const container = document.getElementById('chama-list-sidebar');
        if (!container) {
            console.error("CRITICAL: Element #chama-list-sidebar was not found in the HTML.");
            return;
        }

        // Force display
        container.innerHTML = groups.map(g => `
            <div class="nav-item">
                <a class="nav-link-custom ps-4" onclick="loadGroupView(${g.id}, 'members')">
                    <i class="bi bi-bank"></i> ${g.name}
                </a>
            </div>
        `).join('');
    }
}

function showDashboard() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('dashboard-ui').style.display = 'block';
    document.getElementById('display-name').innerText = `Hi, ${localStorage.getItem('username')}`;
    loadSidebarChamas();
}

function logout() {
    localStorage.clear();
    window.location.reload();
}

function showInviteModal() {
    document.getElementById('modalTitle').innerText = 'Invite Member';
    document.getElementById('modalBody').innerHTML = `
        <input type="text" id="invite-phone" class="form-control" placeholder="Enter phone number">
    `;
    document.getElementById('modalSubmit').onclick = handleInvite;
    actionModal.show();
}

// Function to fetch and display contributions for the group
async function fetchGroupContributions(groupId) {
    const res = await fetch(`${API_BASE}/contributions/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    if (res.ok) {
        const contributions = await res.json();
        const groupContributions = contributions.filter(c => c.group == groupId);
        const tableBody = document.getElementById('contribution-list');
        tableBody.innerHTML = groupContributions.length ? groupContributions.map(c => `
            <tr>
                <td>${c.member_name}</td>
                <td>KES ${c.amount}</td>
                <td>Completed</td>  <!-- Assuming all contributions are completed; adjust if needed -->
            </tr>
        `).join('') : '<tr><td colspan="3" class="text-center text-muted py-3">No recent contributions</td></tr>';
    }
}

// Function to handle contributions (Mocked for now as we'd need a Contribution model/viewset)
async function handleContribution() {
    console.log("handleContribution called, currentGroupId:", currentGroupId);  // Debug log
    if (!currentGroupId) {
        alert("No group selected.");
        return;
    }
    const amount = prompt("Enter contribution amount (KES):");
    if (!amount || isNaN(amount)) return;

    console.log("Posting contribution:", { group: currentGroupId, amount: parseFloat(amount) });  // Debug log
    const res = await fetch(`${API_BASE}/contributions/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ group: currentGroupId, amount: parseFloat(amount) })
    });

    if (res.ok) {
        alert("Contribution added!");
        loadGroupView(currentGroupId);  // Refresh UI
    } else {
        const error = await res.json();
        console.error("Contribution failed:", error);  // Debug log
        alert("Failed to add contribution: " + (error.detail || "Unknown error"));
    }
}

async function handleRequestLoan() {
    console.log("handleRequestLoan called, currentGroupId:", currentGroupId);  // Debug log
    if (!currentGroupId) {
        alert("No group selected.");
        return;
    }
    const amount = prompt("Enter loan amount (KES):");
    if (!amount || isNaN(amount)) return;

    console.log("Posting loan:", { group: currentGroupId, amount: parseFloat(amount) });  // Debug log
    const res = await fetch(`${API_BASE}/loans/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ group: currentGroupId, amount: parseFloat(amount) })
    });

    if (res.ok) {
        alert("Loan request submitted!");
        fetchGroupLoans(currentGroupId);  // Refresh loans table
    } else {
        const error = await res.json();
        console.error("Loan request failed:", error);  // Debug log
        alert("Failed to request loan: " + (error.detail || "Unknown error"));
    }
}

// Function to fetch and display loans for the specific group
async function fetchGroupLoans(groupId) {
    const res = await fetch(`${API_BASE}/loans/`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });

    if (res.ok) {
        const loans = await res.json();
        const groupLoans = loans.filter(l => l.group == groupId);
        const tableBody = document.getElementById('loan-list-table');

        tableBody.innerHTML = groupLoans.length ? groupLoans.map(l => `
            <tr>
                <td><i class="bi bi-person me-2"></i>User ${l.borrower}</td>
                <td>KES ${l.amount}</td>
                <td>${l.interest_rate}%</td>
                <td class="fw-bold">KES ${l.total_to_pay}</td>
                <td>
                    <span class="badge ${l.status === 'APPROVED' ? 'bg-success' : 'bg-warning text-dark'}">
                        ${l.status}
                    </span>
                </td>
                <td>
                    ${l.status === 'PENDING' ?
                `<button class="btn btn-sm btn-success py-0" onclick="approveLoan(${l.id})">Approve</button>` :
                `<i class="bi bi-check-all text-success"></i>`
            }
                </td>
            </tr>
        `).join('') : '<tr><td colspan="6" class="text-center py-4">No loan requests found</td></tr>';
    }
}

// Function to approve a loan using your PATCH action in views.py
async function approveLoan(loanId) {
    if (!confirm("Are you sure you want to approve and disburse this loan?")) return;

    const res = await fetch(`${API_BASE}/loans/${loanId}/approve/`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });

    if (res.ok) {
        alert("Loan Approved! Funds have been deducted from the group balance.");
        loadGroupView(currentGroupId);
    } else {
        const err = await res.json();
        alert("Error: " + (err.error || "Could not approve loan"));
    }
}

// HandleInvite function
async function handleInvite() {
    const phone = document.getElementById('invite-phone').value;
    if (!phone) return;

    const res = await fetch(`${API_BASE}/groups/${currentGroupId}/invite/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ phone })
    });

    if (res.ok) {
        alert("Invite sent!");
        actionModal.hide();
        loadGroupView(currentGroupId); // Refresh UI
    } else {
        const error = await res.json();
        alert("Failed to send invite: " + (error.error || "Unknown error"));
    }
}