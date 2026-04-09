import os
import uuid

from flask import Blueprint, jsonify, request, current_app, send_file
from extensions import socketio, db
from models import User
from models.current_incident_models import CurrentIncident, IncidentSeverity, CurrentIncidentMission, \
    CurrentIncidentStatusSeverityHistory, CurrentIncidentMissionStatusHistory, CurrentIncidentManager, \
    CurrentIncidentPhoto, CurrentIncidentMissionEmployee
from models.incident_base_models import IncidentType, IncidentTypeMission
from models.sectors import Branch, SectorManagement, SectorBranch, SectorClassification
from datetime import datetime
from routes.common import commit_trial, add_tokens_to_group, send_incident_notification, private_route_for_auth_level


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
@private_route_for_auth_level(0)
def add_current_incident(current_user):
    all_types = IncidentType.query.all()
    all_types_list = [t.to_dict() for t in all_types]
    all_severities = IncidentSeverity.query.all()
    all_severities_list = [s.to_dict() for s in all_severities]
    branches = Branch.query.all()
    branches_list = [branch.to_dict() for branch in branches]
    if request.method == "POST":
        data = request.get_json()
        now = datetime.now()
        new_current_incident = CurrentIncident(
            current_incident_description=data["current_incident_description"],
            current_incident_type_id=data["current_incident_type_id"],
            current_incident_created_by=current_user.user_id,
            current_incident_created_at=now,
            current_incident_severity=data["current_incident_severity"],
            current_incident_severity_updated_by=current_user.user_id,
            current_incident_severity_updated_at=now,
            current_incident_status_updated_by=current_user.user_id,
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

        if not predefined_missions:
            db.session.rollback()
            return jsonify({
                "error": "لا يمكن انشاء أزمة ليس لها مهمات مسجلة مسبقا"
            }), 400

        for m in predefined_missions:
            db.session.add(CurrentIncidentMission(
                current_incident_id=new_current_incident.current_incident_id,
                current_incident_mission_id=m.mission_id,  # from IncidentTypeMission table
                current_incident_mission_order=m.mission_order,  # from IncidentTypeMission table
                current_incident_mission_status=1,  # reported
            ))

        manager = assign_incident_manager(new_current_incident)

        if manager:
            # print(manager.to_dict())
            new_current_incident.manager_id = manager.user_id
            assignment = CurrentIncidentManager(
                current_incident_id=new_current_incident.current_incident_id,
                user_id=manager.user_id,
                assigned_by=1, # system
                assigned_at=now
            )
            db.session.add(assignment)
        else:
            db.session.rollback()
            return jsonify({
                "error": "لم يتم انشاء الأزمة، لا يوجد مديرين صالحين في الوقت الحالي"
            }), 400

        def after_commit():
            socketio.emit("incident_created", new_current_incident.to_dict())
            device_tokens = [tok.token for tok in manager.tokens if tok.token]
            if device_tokens:
                # print("there are tokens")
                add_tokens_to_group(
                    device_tokens,
                    f"Team_incident_{new_current_incident.current_incident_id}")

        result = commit_trial("تم إضافة الأزمة بنجاح", on_success=after_commit)

        # send notification after commit, outside the callback
        if result[1] == 200:
            send_incident_notification.delay(
                incident_id=new_current_incident.current_incident_id,
                event="أزمة جديدة",
                body=f"تم تعيينك مديراً لازمة {new_current_incident.current_incident_description}",
                data={
                    "incident_id": str(new_current_incident.current_incident_id),
                    "type": "incident_created"
                }
            )
        return result

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



@current_incident_bp.route("/upload-incident-photo/<int:incident_id>", methods=["POST"])
def upload_incident_photo(incident_id):
    if request.method == "POST":
        current_incident = CurrentIncident.query.get_or_404(incident_id)
        file = request.files.get("photo")
        description = request.form.get("description")
        # TODO: Add user_id from session
        user_id = 1

        if not file:
            return {"error": "لا يوجد صور، لم يتم الحفظ"}, 400

        # Generate unique filename
        extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{extension}"

        # Define upload folder
        upload_folder = os.path.join(r"D:\IMS_UPLOADS", "uploads", "incidents", str(incident_id))
        os.makedirs(upload_folder, exist_ok=True)

        # Full path
        full_path = os.path.join(upload_folder, filename)

        # Save file to disk
        file.save(full_path)

        # Save relative path in DB
        relative_path = os.path.join("uploads", "incidents", str(incident_id), filename)

        photo = CurrentIncidentPhoto(
            current_incident_id=incident_id,
            file_path=relative_path,
            description=description,
            current_incident_photo_uploaded_by=user_id,
            current_incident_photo_uploaded_at=datetime.now(),
            current_incident_status=current_incident.current_incident_status,
            x_axis=request.form.get("x_axis"),
            y_axis=request.form.get("y_axis")
        )
        db.session.add(photo)
        def emit_update():
            socketio.emit("incident_updated", photo.incident.to_dict())
        return commit_trial("تم إضافة الصورة بنجاح", on_success=emit_update)
    return jsonify({"response": "سبحان الله وبحمده سبحان الله العظيم"})


@current_incident_bp.route("/incident-photos/<int:incident_id>", methods=["GET"])
def get_incident_photos(incident_id):

    photos = CurrentIncidentPhoto.query.filter_by(
        current_incident_id=incident_id
    ).all()
    photos_list = [photo.to_dict() for photo in photos]
    print(photos_list)
    return jsonify(photos_list)


@current_incident_bp.route("/view-incident-photo/<int:photo_id>")
def view_incident_photo(photo_id):

    photo = CurrentIncidentPhoto.query.get_or_404(photo_id)

    full_path = os.path.join(r"D:\IMS_UPLOADS", photo.file_path)

    return send_file(full_path)


@current_incident_bp.route("/mission-user-assign/<int:current_incident_id>", methods=["GET", "POST"])
def mission_user_assign(current_incident_id):
    users = User.query.filter(User.is_active == True).all()
    users_list = [user.to_dict() for user in users]
    incident = CurrentIncident.query.get_or_404(current_incident_id)
    # TODO: validate that current user is the current incident manager
    # if incident.manager_id != current_user.user_id:
    # return you are not the manager
    if incident.current_incident_status > 5:
        return jsonify({"error": "لا يمكن تعيين موظفين لازمة مغلقة"}), 400
    if request.method == "POST":
        data = request.get_json()
        now = datetime.now()
        print(data)

        db.session.add_all(
            [
                CurrentIncidentMissionEmployee(
                    current_incident_mission_id=obj["mission_id"],
                    current_incident_mission_emp=obj["user_id"],
                    current_incident_mission_assigned_by=incident.manager_id,
                    current_incident_mission_assigned_at=now
                )
                for obj in data
            ]
        )
        mission_ids = {obj["mission_id"] for obj in data}
        for mission in incident.missions:
            if mission.id in mission_ids:
                mission.current_incident_mission_status = 2 # assigned
                mission.current_incident_mission_status_updated_by = incident.manager_id
                mission.current_incident_mission_status_updated_at = now
        # TOTHINK: should user accept multiple missions?

        def emit_update():
            socketio.emit("incident_updated", incident.to_dict())
        return commit_trial("تم تعيين الموظفين بنجاح", on_success=emit_update)
    return jsonify({"response": "لا حول ولا قوة إلا بالله العلي العظيم"})


