from flask_socketio import emit
from extensions import socketio
from models.current_incident_models import CurrentIncident


def get_current_incidents():
    active_statuses = [1, 2, 3, 4, 5]
    return (
        CurrentIncident.query
        .filter(CurrentIncident.current_incident_status.in_(active_statuses))
        .order_by(CurrentIncident.current_incident_created_at.desc())
        .all()
    )

@socketio.on("connect")
def handle_connect(auth):
    print("Client connected")

    # Send current incident immediately
    incidents = get_current_incidents()
    incidents_list = [i.to_dict() for i in incidents]
    print(incidents_list)
    emit("incident_snapshot", incidents_list)


@socketio.on("join_incident")
def join_incident(data):
    incident_id = data["incident_id"]
    print(f"Client joined incident {incident_id}")


