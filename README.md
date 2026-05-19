# Incident Management System

A real-time incident tracking and management platform built with Python, Flask, and SocketIO. Designed for operational environments requiring fast incident response, automated assignment, and hierarchical escalation.

## Features

- **Real-time incident tracking** via WebSocket (Flask-SocketIO)
- **Automated incident assignment** — automatically assigns the most available manager on incident creation
- **Role-based access control** with JWT authentication
- **Hierarchical escalation mechanism** for efficient issue resolution
- **Push notifications** to assigned managers via device tokens
- **Mission-based workflows** — each incident type has predefined missions auto-assigned on creation
- **Status & severity history tracking** for full audit trail
- **Background task processing** — incidents are queued and processed asynchronously without blocking the main thread
- **Production-ready** — served via Waitress WSGI server with proper DB session management

## Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO
- **Database:** SQLAlchemy ORM (SQL Server)
- **Authentication:** JWT (JSON Web Tokens)
- **Server:** Waitress (production WSGI server)
- **Real-time:** WebSocket via SocketIO
- **Notifications:** Firebase Cloud Messaging (FCM) via device token groups

## Project Structure

```
incident-management-system/
├── main.py                  # App entry point, background task listener
├── extensions.py            # Shared extensions (db, socketio)
├── models/
│   ├── current_incident_models.py      # Incident, Mission, Manager, History models
│   ├── incident_base_models.py         # Base/reference data models
│   └── cms_meta_data.py                # Temp incident queue model
├── routes/
│   ├── __init__.py                     # App factory
│   ├── common.py                       # Shared utilities, notifications
│   └── current_incidents.py            # Incident API endpoints
└── .gitignore
```

## How It Works

1. An incident is submitted and stored in a temporary queue (`CurrentIncidentTemp`)
2. A background task continuously polls the queue for unprocessed incidents
3. On detection, the system:
   - Creates a full incident record
   - Auto-assigns predefined missions based on incident type
   - Assigns the most available manager
   - Records status and severity history
   - Emits a real-time WebSocket event to connected clients
   - Sends push notifications to the assigned manager's devices
4. The temp record is marked as processed

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/incidents` | Create new incident |
| GET | `/incidents` | List all incidents |
| PUT | `/incidents/<id>` | Update incident status/severity |
| GET | `/incidents/<id>/missions` | Get incident missions |

> Full API documentation available on request.

## Setup & Installation

```bash
# Clone the repository
git clone https://github.com/Hosamalsamman/incident-management-system.git
cd incident-management-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install flask flask-socketio flask-sqlalchemy flask-jwt-extended waitress

# Configure database connection in extensions.py

# Run the application
python main.py
```

## Key Implementation Details

- **DB session cleanup** on every background loop iteration to prevent connection pool exhaustion
- **Optimistic locking** on temp incidents (`processed = None`) to prevent duplicate processing
- **Graceful error handling** with full traceback logging and session rollback on failure
- **Non-blocking notifications** — sent via background tasks to avoid delaying incident processing

## Author

**Hossam Al-Samman** — Backend & Data Engineer  
[GitHub](https://github.com/Hosamalsamman) | [LinkedIn](https://linkedin.com/in/hossam-alsamman)
