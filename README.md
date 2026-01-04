# Stax Chama - Digital Micro-Finance Application

A modern web-based platform for managing community savings groups (Chamas) with features for contributions, loans, and member management.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Usage Guide](#-usage-guide)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [License](#-license)

---

## ✨ Features

### Authentication & User Management
* **Registration:** Phone number and national ID verification.
* **Security:** Secure JWT-based authentication.
* **RBAC:** Role-based access control (Members vs. Chairman).

### Chama (Group) Management
* **Group Creation:** Create and manage multiple savings groups.
* **Invitations:** Add members via phone number with a pending approval workflow.
* **Financial Tracking:** Real-time group balance tracking and member lists.

### Contributions
* **Recording:** Record individual contributions.
* **Automation:** Automatic group balance updates upon contribution.
* **History:** Full tracking of contribution dates and member details.

### Loan Management
* **Requests:** Simple loan application process.
* **Interest:** Fixed 10% interest rate and total repayment calculation.
* **Workflow:** Approval workflow with automatic fund disbursement and balance deduction.

### Dashboard Analytics
* **Overview:** Financial health and member statistics.
* **Visuals:** Loan distribution and monthly contribution trends via Chart.js.

---

## 🛠 Tech Stack

**Backend:**
* Django 5.2.9 (Framework)
* Django REST Framework 3.16.1 (API)
* SimpleJWT 5.5.1 (Auth)
* PostgreSQL / SQLite (Database)

**Frontend:**
* Vanilla JavaScript (ES6+)
* Bootstrap 5.3.0 (UI/Responsive)
* Chart.js (Analytics)

---

## 📁 Project Structure

```text
Stax-Chama-app/
├── core/                # Django project settings
│   ├── settings.py      # Project configuration
│   ├── urls.py          # Project-level routing
├── api/                 # Django app (Backend Logic)
│   ├── models.py        # Database models
│   ├── views.py         # API endpoints & Logic
│   ├── serializers.py   # Data validation/transformation
│   └── urls.py          # API routes
├── static/              # Frontend files
│   ├── index.html       # Main UI
│   ├── app.js           # Frontend logic
│   └── style.css        # Custom styles
├── requirements.txt     # Python dependencies
├── vercel.json          # Deployment config
└── manage.py            # Django CLI

## 🚀 Installation

### Prerequisites
* **Python 3.8+**
* **pip** (Python package manager)
* **Git**
* **PostgreSQL** (Optional for local, required for production)

Step 1: Clone the Repository
```bash
git clone [https://github.com/yourusername/Stax-Chama-app.git](https://github.com/yourusername/Stax-Chama-app.git)
cd Stax-Chama-app

Step 2: Virtual Environment Setup
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
pip install -r requirements.txt

Step 4: Database & Admin Setup
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin access)
python manage.py createsuperuser

Step 5: Local Configuration
Create a .env file in the project root:
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

⚙️ Configuration
JWT Settings (settings.py)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS Setup
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "[https://your-vercel-domain.vercel.app](https://your-vercel-domain.vercel.app)",
]

## 📡 API Documentation

### Authentication Endpoints
| Action | Method | Endpoint | Payload |
|:---|:---|:---|:---|
| **Login** | `POST` | `/api/token/` | `{"username": "", "password": ""}` |
| **Register** | `POST` | `/api/register/` | `{"username": "", "password": "", "phone_number": "", "national_id": ""}` |

### Chama & Finance Endpoints
| Action | Method | Endpoint | Note |
|:---|:---|:---|:---|
| **List Groups** | `GET` | `/api/groups/` | Returns groups user is a member of |
| **Group Summary** | `GET` | `/api/groups/{id}/summary/` | Balance and member data |
| **Add Saving** | `POST` | `/api/contributions/` | `{"group": id, "amount": decimal}` |
| **Request Loan** | `POST` | `/api/loans/` | `{"group": id, "amount": decimal}` |
| **Approve Loan** | `PATCH` | `/api/loans/{id}/approve/` | Admin only: Deducts from balance |

---

💡 Usage Guide
Member Onboarding: Users must register with a unique phone number before they can be invited to a group.

Chairmanship: The user who creates a group is automatically set as the Chairman.

Invitations: Chairmen invite members via phone number. The system links the user to the group instantly.

Contributions: Once a contribution is posted, the Group Balance updates in real-time across all member dashboards.

Loans: Loans are created with a PENDING status. Only when a Chairman clicks Approve is the 10% interest applied and the principal deducted from the Chama treasury.

## 🔧 Troubleshooting

| Issue | Cause | Solution |
|:---|:---|:---|
| **Chamas not displaying** | Sidebar state mismatch | Ensure `app.js` calls `loadSidebarChamas()` in `showDashboard()` |
| **401 Unauthorized** | Token expired/Invalid | Log out and log back in; check for `Bearer ` prefix in headers |
| **Empty Summary** | Database null fields | Run `python manage.py migrate` and check object existence |
| **Loan Approval Failed** | Insufficient Funds | Ensure Group Balance ≥ Loan Principal |

---

🚀 Deployment (Vercel)
Environment Variables: In Vercel, navigate to Settings > Environment Variables and add:

DJANGO_SECRET_KEY

DATABASE_URL (from your PostgreSQL provider)

DEBUG = False

Static Files: Ensure whitenoise is in MIDDLEWARE to handle CSS/JS on the cloud.

Database: Run python manage.py migrate using the Vercel CLI or a custom deployment script to initialize your production tables.

📄 License
This project is licensed under the MIT License.

Status: Version 1.0.0 - Production Ready 
Maintained by: Ryki Solutions