from flask import Blueprint, jsonify, request
from extensions import socketio, db
from models import User
from models.current_incident_models import CurrentIncident, IncidentSeverity, CurrentIncidentMission, \
    CurrentIncidentStatusSeverityHistory, CurrentIncidentMissionStatusHistory, CurrentIncidentManager
from models.incident_base_models import IncidentType, IncidentTypeMission
from models.sectors import Branch, SectorManagement, SectorBranch, SectorClassification
from datetime import datetime
from routes.common import commit_trial

def assign_incident_manager(incident):
    return (
        User.query
        .join(SectorManagement)
        .filter(
            User.is_active == True,

            # 🔥 Level 2 = Incident Manager
            SectorManagement.authority_level_id >= 2,

            # User level must match sector level
            User.authority_level_id == SectorManagement.authority_level_id,

            # Sector handles branch
            SectorManagement.sector_branches.any(
                SectorBranch.branch_id == incident.branch_id
            ),

            # Sector handles classification
            SectorManagement.classifications.any(
                SectorClassification.class_id == incident.incident_type.class_id
            ),
        )
        .order_by(User.authority_level_id.asc())
        .first()
    )


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
    branches = Branch.query.all()
    branches_list = [branch.to_dict() for branch in branches]
    if request.method == "POST":
        data = request.get_json()
        now = datetime.now()
        # TODO: add real user id instead of 1
        new_current_incident = CurrentIncident(
            current_incident_description=data["current_incident_description"],
            current_incident_type_id=data["current_incident_type_id"],
            current_incident_created_by=1,
            current_incident_created_at=now,
            current_incident_severity=data["current_incident_severity"],
            current_incident_severity_updated_by=1,
            current_incident_severity_updated_at=now,
            current_incident_status_updated_by=1,
            current_incident_status=1,
            current_incident_status_updated_at=now,
            current_incident_x_axis=data["current_incident_x_axis"],
            current_incident_y_axis=data["current_incident_y_axis"],
            current_incident_notes=data["current_incident_notes"],
            branch_id=data["branch_id"],
        )
        # print("after create: ", new_current_incident.current_incident_id)  None
        db.session.add(new_current_incident)
        # print("after add: ", new_current_incident.current_incident_id)     None
        # Fetch predefined missions for this incident type
        db.session.flush()
        predefined_missions = IncidentTypeMission.query.filter_by(
            incident_type_id=new_current_incident.current_incident_type_id
        ).all()
        # print("after query: ", new_current_incident.current_incident_id)   id generated as session.flush happened when query

        for m in predefined_missions:
            db.session.add(CurrentIncidentMission(
                current_incident_id=new_current_incident.current_incident_id,
                current_incident_mission_id=m.mission_id,  # from IncidentTypeMission table
                current_incident_mission_order=m.mission_order,  # from IncidentTypeMission table
                current_incident_mission_status=1,  # reported
            ))

        if not predefined_missions:
            db.session.rollback()
            return jsonify({
                "error": "لا يمكن انشاء أزمة ليس لها مهمات مسجلة مسبقا"
            }), 400

        manager = assign_incident_manager(new_current_incident)

        if manager:
            assignment = CurrentIncidentManager(
                current_incident_id=new_current_incident.current_incident_id,
                user_id=manager.user_id,
                assigned_by=1, # system
                assigned_at=now
            )
            db.session.add(assignment)

        def after_commit():
            print("New incident added:", new_current_incident.to_dict())
            socketio.emit("incident_created", new_current_incident.to_dict())

        return commit_trial("تم إضافة الأزمة بنجاح", on_success=after_commit)

    return jsonify(types=all_types_list, severities=all_severities_list, branches=branches_list)


@current_incident_bp.route("/edit-current-incident/<current_incident_id>", methods=["GET","POST"])
def edit_current_incident(current_incident_id):
    current_incident = CurrentIncident.query.get(current_incident_id)
    if request.method == "POST":
        data = request.get_json()
        print(data)
        should_log_history = False
        now = datetime.now()

        current_incident.current_incident_description = data["current_incident_description"]
        current_incident.current_incident_x_axis = data["current_incident_x_axis"]
        current_incident.current_incident_y_axis = data["current_incident_y_axis"]
        # TODO: replace 1 with current user
        if current_incident.current_incident_severity != data["current_incident_severity"]:
            current_incident.current_incident_severity = data["current_incident_severity"]
            current_incident.current_incident_severity_updated_by = 1
            current_incident.current_incident_severity_updated_at = now
            should_log_history = True

        if current_incident.current_incident_status != data["current_incident_status"]:
            current_incident.current_incident_status = data["current_incident_status"]
            current_incident.current_incident_status_updated_by = 1
            current_incident.current_incident_status_updated_at = now
            should_log_history = True

        print(current_incident.to_dict())
        # insert in history
        if should_log_history:
            new_hist = CurrentIncidentStatusSeverityHistory(
                current_incident_id=current_incident.current_incident_id,
                current_incident_status=current_incident.current_incident_status,
                current_incident_status_changed_by=current_incident.current_incident_status_updated_by,
                current_incident_status_changed_at=now,
                current_incident_severity=current_incident.current_incident_severity,
                current_incident_severity_changed_by=current_incident.current_incident_severity_updated_by,
                current_incident_severity_changed_at=now
            )
            db.session.add(new_hist)

        def emit_update():
            socketio.emit("incident_updated", current_incident.to_dict())
        return commit_trial("تم تعديل البيانات بنجاح", on_success=emit_update)
    return jsonify({"response": "اللهم صل على سيدنا محمد"})


@current_incident_bp.route("/edit-current-mission/<current_incident_id>/<current_mission_id>/<mission_order>", methods=["GET","POST"])
def edit_current_mission(current_incident_id, current_mission_id, mission_order):
    current_mission = (
        CurrentIncidentMission.query
        .filter_by(
            current_incident_id=current_incident_id,
            current_incident_mission_id=current_mission_id,
            current_incident_mission_order=mission_order
        )
        .first()
    )
    if not current_mission:
        return jsonify({"error": "المهمة غير موجودة"}), 404

    if request.method == "POST":
        data = request.get_json()
        now = datetime.now()
        old_status = current_mission.current_incident_mission_status

        #TODO: add current user instead of 1
        if old_status == data["current_incident_mission_status"]:
            return jsonify({"error": "لم يتم تغيير الحالة"}), 400
        current_mission.current_incident_mission_status = data["current_incident_mission_status"]
        current_mission.current_incident_mission_status_updated_by = 1
        current_mission.current_incident_mission_status_updated_at = now

        new_mission_hist = CurrentIncidentMissionStatusHistory(
            current_incident_mission_id=current_mission.id,
            current_incident_mission_status=current_mission.current_incident_mission_status,
            current_incident_mission_status_updated_by=current_mission.current_incident_mission_status_updated_by,
            current_incident_mission_status_updated_at=now,
        )
        db.session.add(new_mission_hist)

        def emit_update():
            socketio.emit("mission_updated", current_mission.to_dict())

        return commit_trial("تم تعديل البيانات بنجاح", on_success=emit_update)
    return jsonify({"response": "اللهم صل على سيدنا محمد"})


