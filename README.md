# ⚗️ Chemical Equipment Parameter Visualizer

A full-stack web application for visualizing and analyzing chemical equipment parameters. Upload CSV files containing equipment data, view interactive charts, generate PDF reports, and track upload history.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![React](https://img.shields.io/badge/React-18.2-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌐 Live Demo

🔗 **[View Live Application](https://chemical-equipment-app.onrender.com)**


---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **CSV Upload** | Drag-and-drop or click to upload equipment data |
| 📊 **Data Visualization** | Interactive pie, bar, and line charts |
| 📋 **Data Table** | Sortable and searchable table view |
| 📈 **Statistics** | Automatic calculation of avg, min, max, std deviation |
| 📄 **PDF Reports** | Generate and download professional PDF reports |
| 🕐 **Upload History** | Track last 5 uploaded datasets |
| 🔐 **Authentication** | User registration and login system |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |
| 🖥️ **Desktop App** | PyQt5 desktop application (optional) |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.11 | Programming language |
| Django 4.2 | Web framework |
| Django REST Framework | REST API |
| Pandas | CSV parsing & data analysis |
| ReportLab | PDF generation |
| PostgreSQL | Production database |
| Gunicorn | WSGI server |
| WhiteNoise | Static file serving |

### Frontend (Web)
| Technology | Purpose |
|------------|---------|
| React 18 | UI library |
| Axios | HTTP client |
| Chart.js | Data visualization |
| CSS3 | Styling |

### Frontend (Desktop)
| Technology | Purpose |
|------------|---------|
| PyQt5 | Desktop UI framework |
| Matplotlib | Charts |
| Requests | HTTP client |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (for production) or SQLite (for development)

### Local Development

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer
2️⃣ Setup Backend
Bash

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
Backend will be running at: http://localhost:8000

3️⃣ Setup Frontend
Bash

# Open new terminal
cd frontend-web

# Install dependencies
npm install

# Start development server
npm start
Frontend will be running at: http://localhost:3000
Render - Deployment platform
