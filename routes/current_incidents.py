from flask import Blueprint, jsonify, request
from extensions import socketio, db
from models.current_incident_models import CurrentIncident, IncidentSeverity, CurrentIncidentMission
from models.incident_base_models import IncidentType, IncidentTypeMission
from datetime import datetime
from routes.common import commit_trial


current_incident_bp = Blueprint("current_incident", __name__)


@current_incident_bp.route("/current-incidents")
def all_current_incidents():
    current_incidents = CurrentIncident.query.all()
    current_incidents_list = [c.to_dict() for c in current_incidents]
    return jsonify(current_incidents_list)


@current_incident_bp.route("/add-current-incident", methods=["GET","POST"])
def add_current_incident():
    all_types = IncidentType.query.all()
    all_types_list = [t.to_dict() for t in all_types]
    all_severities = IncidentSeverity.query.all()
    all_severities_list = [s.to_dict() for s in all_severities]
    if request.method == "POST":
        data = request.get_json()
        # TODO: add real user id instead of 1
        new_current_incident = CurrentIncident(
            current_incident_description=data["current_incident_description"],
            current_incident_type_id=data["current_incident_type_id"],
            current_incident_created_by=1,
            current_incident_created_at=datetime.now(),
            current_incident_severity=data["current_incident_severity"],
            current_incident_severity_updated_by=1,
            current_incident_severity_updated_at=datetime.now(),
            current_incident_status_updated_by=1,
            current_incident_status=1,
            current_incident_status_updated_at=datetime.now(),
            current_incident_x_axis=data["current_incident_x_axis"],
            current_incident_y_axis=data["current_incident_y_axis"],
            current_incident_notes=data["current_incident_notes"]
        )
        db.session.add(new_current_incident)
        # Fetch predefined missions for this incident type
        predefined_missions = IncidentTypeMission.query.filter_by(
            incident_type_id=new_current_incident.current_incident_type_id
        ).all()

        for m in predefined_missions:
            db.session.add(CurrentIncidentMission(
                current_incident_id=new_current_incident.current_incident_id,
                current_incident_mission_id=m.mission_id,  # from IncidentTypeMission table
                current_incident_mission_order=m.mission_order,  # from IncidentTypeMission table
                current_incident_mission_status=1,  # reported
            ))

        def after_commit():
            print("New incident added:", new_current_incident.to_dict())
            socketio.emit("incident_created", new_current_incident.to_dict())

        return commit_trial("تم إضافة الأزمة بنجاح", on_success=after_commit)

    return jsonify(types=all_types_list, severities=all_severities_list)


@current_incident_bp.route("/edit-current-incident/<current_incident_id>", methods=["GET","POST"])
def edit_current_incident(current_incident_id):
    current_incident = CurrentIncident.query.get(current_incident_id)
    if request.method == "POST":
        data = request.get_json()
        current_incident.current_incident_description = data["current_incident_description"]

        def emit_update():
            socketio.emit("incident_updated", current_incident.to_dict())
        return commit_trial("تم تعديل البيانات بنجاح", on_success=emit_update)
    return jsonify({"response": "اللهم صل على سيدنا محمد"})