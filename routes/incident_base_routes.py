from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DataError

from models.incident_base_models import IncidentType, Classification, Mission, IncidentTypeMission
from flask import Blueprint, jsonify, request
from models import db
from routes.common import commit_trial

incident_base_bp = Blueprint("incident_base", __name__)


@incident_base_bp.route("/all-incident-types")
def all_incident_types():
    incident_types = IncidentType.query.all()
    incident_types_list = [i_type.to_dict() for i_type in incident_types]
    # print(incident_types_list)
    return jsonify(incident_types_list)


@incident_base_bp.route("/edit-incident-type/<type_id>", methods=["GET", "POST"])
def edit_incident_type(type_id):
    incident_type = IncidentType.query.get(type_id)
    classes = db.session.query(Classification).all()
    classes_list = [c.to_dict() for c in classes]
    if request.method == "POST":
        data = request.get_json()
        incident_type.incident_type_name = data["incident_type_name"]
        incident_type.classification = data["classification"]
        return commit_trial("تم تعديل نوع الأزمة بنجاح")
    return jsonify(classes_list)


@incident_base_bp.route("/add-incident-type", methods=["GET", "POST"])
def add_incident_type():
    classes = db.session.query(Classification).all()
    classes_list = [c.to_dict() for c in classes]
    if request.method == "POST":
        data = request.get_json()
        print(data)
        new_incident_type = IncidentType(
            incident_type_name=data["incident_type_name"],
            class_id=data["class_id"],
        )
        db.session.add(new_incident_type)
        return commit_trial("تم إضافة أزمة جديدة بنجاح")
    return jsonify(classes_list)


@incident_base_bp.route("/all-missions")
def all_missions():
    missions = Mission.query.all()
    missions_list = [mission.to_dict() for mission in missions]
    return jsonify(missions_list)


@incident_base_bp.route("/edit-mission/<mission_id>", methods=["GET", "POST"])
def edit_mission(mission_id):
    current_mission = Mission.query.get(mission_id)
    classes = Classification.query.all()
    c_list = [c.to_dict() for c in classes]
    if request.method == "POST":
        data = request.get_json()
        current_mission.mission_name = data["mission_name"]
        current_mission.class_id = data["class_id"]
        return commit_trial("تم تعديل المهمة بنجاح")

    return jsonify(c_list)


@incident_base_bp.route("/new-mission", methods=["GET", "POST"])
def add_new_mission():
    classes = Classification.query.all()
    classes_list = [c.to_dict() for c in classes]
    if request.method == "POST":
        data = request.get_json()
        new_mission = Mission(
            mission_name=data["mission_name"],
            class_id=data["class_id"],
        )
        db.session.add(new_mission)
        return commit_trial("تم إضافة مهمة جديدة بنجاح")

    return jsonify(classes_list)


@incident_base_bp.route("/incident-type-missions")
def get_incident_type_missions():
    incident_missions = IncidentTypeMission.query.all()
    i_m_list = [i_m.to_dict() for i_m in incident_missions]
    return jsonify(i_m_list)


@incident_base_bp.route("/edit-incident-type-mission/<incident_id>/<mission_id>", methods=["GET", "POST"])
def edit_incident_type_mission(incident_id, mission_id):
    incident_mission = IncidentTypeMission.query.get(incident_id, mission_id)
    if request.method == "POST":
        data = request.get_json()
        incident_mission.incident_type_id = data["incident_type_id"]
        incident_mission.mission_id = data["mission_id"]
        incident_mission.mission_order = data["mission_order"]
        return commit_trial("تم تعديل البيانات بنجاح")

    return jsonify({"response": "استغفر الله"})


@incident_base_bp.route("/assign-incident-type-missions", methods=["GET", "POST"])
def add_new_incident_type_mission():
    incident_types = IncidentTypeMission.query.all()
    missions = Mission.query.all()
    classes = Classification.query.all()
    if request.method == "POST":
        data = request.get_json()
        print(data)
        # new_i_t_m = IncidentTypeMission(
        #     incident_type_id=data["incident_type_id"],
        #     mission_id=data["mission_id"],
        #     mission_order=data["mission_order"]
        # )
        # db.session.add(new_i_t_m)
        # return commit_trial("تم إضافة البيانات بنجاح")
        try:
            old = IncidentTypeMission.query.filter_by(
                incident_type_id=data["incident_type"]
            ).all()

            for m in old:
                db.session.delete(m)

            db.session.add_all([
                IncidentTypeMission(
                    incident_type_id=data["incident_type"],
                    mission_id=m["mission_id"],
                    mission_order=m["order"]
                )
                for m in data["missions"]
            ])

            return commit_trial("تم التحديث بنجاح")

        except Exception:
            db.session.rollback()
            raise

    return jsonify(incident_types=incident_types, missions=missions, classes=classes)