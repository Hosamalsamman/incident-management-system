from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room
from extensions import socketio, db, app
from models import User
from models.current_incident_models import CurrentIncident, IncidentParticipant
import json

def get_current_incidents_for_user(user_id):
    active_statuses = [1, 2, 3, 4, 5]
    incident_ids = (
        db.session.query(IncidentParticipant.incident_id)
        .filter(IncidentParticipant.user_id == user_id)
        .scalar_subquery()
    )
    return (
        CurrentIncident.query
        .filter(
            CurrentIncident.current_incident_status.in_(active_statuses),
            CurrentIncident.current_incident_id.in_(incident_ids)
        )
        .order_by(CurrentIncident.current_incident_created_at.desc())
        .all()
    )


def get_user_from_auth(auth):
    try:
        token = auth.get("token") if auth else None
        if not token:
            print("No token provided")
            return None
        decoded = decode_token(token)
        user_id = int(decoded["sub"])  # identity=str(user.user_id) → stored as "sub"
        print(user_id)
        return User.query.get(user_id)
    except Exception:
        return None



connected_sids = {}  # user_id -> sid


def add_user_to_incident(user_id, incident_id, reason):
    if not db.session.get(IncidentParticipant, (incident_id, user_id)):
        db.session.add(IncidentParticipant(
            incident_id=incident_id,
            user_id=user_id,
            added_reason=reason
        ))

    sid = connected_sids.get(user_id)
    if sid:
        try:
            socketio.server.enter_room(sid, f"incident:{incident_id}")
        except (ValueError, KeyError):
            connected_sids.pop(user_id, None)  # stale sid, clean it up


@socketio.on("connect")
def handle_connect(auth):
    user = get_user_from_auth(auth)
    if not user:
        return False

    connected_sids[user.user_id] = request.sid  # track sid

    incident_ids = (
        db.session.query(IncidentParticipant.incident_id)
        .filter(IncidentParticipant.user_id == user.user_id)
        .all()
    )
    for (iid,) in incident_ids:
        join_room(f"incident:{iid}")

    incidents = get_current_incidents_for_user(user.user_id)
    incidents_list = [i.to_dict() for i in incidents]
    print(f"Payload Size: {len(json.dumps(incidents_list))} bytes")
    emit("incident_snapshot", incidents_list)


@socketio.on("disconnect")
def handle_disconnect():
    connected_sids.pop(request.sid, None)  # clean up


@socketio.on("join_incident")
def join_incident(data):
    incident_id = data["incident_id"]
    print(f"Client joined incident {incident_id}")
