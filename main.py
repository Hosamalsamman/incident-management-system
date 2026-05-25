from flask import jsonify

from extensions import socketio
from routes import create_app
from routes.common import dispatch_notification
from extensions import app

create_app()

def listen_to_temp_inserts():
    from datetime import datetime
    from extensions import socketio, db
    from models.cms_meta_data import CurrentIncidentTemp
    from models.current_incident_models import CurrentIncident, CurrentIncidentMission, CurrentIncidentManager, \
        CurrentIncidentStatusSeverityHistory
    from models.incident_base_models import IncidentTypeMission
    from routes.common import commit_trial, dispatch_notification
    from routes.current_incidents import assign_incident_manager

    iteration = 0
    while True:
        iteration += 1
        try:
            with app.app_context():  # ← fresh context every iteration
                temp_incident = CurrentIncidentTemp.query.filter(
                    CurrentIncidentTemp.processed == False
                ).first()

                if temp_incident:
                    print(f"📥 Found incident {temp_incident.cms_case_id}, processing...")
                    temp_incident.processed = None
                    db.session.commit()

                    try:
                        now = datetime.now()
                        new_current_incident = CurrentIncident(
                            current_incident_description=temp_incident.current_incident_description,
                            address=temp_incident.address,
                            current_incident_type_id=temp_incident.current_incident_type_id,
                            current_incident_created_by=1,
                            current_incident_created_at=temp_incident.current_incident_created_at,
                            current_incident_severity=temp_incident.current_incident_severity,
                            current_incident_severity_updated_by=1,
                            current_incident_severity_updated_at=temp_incident.current_incident_severity_updated_at,
                            current_incident_status_updated_by=1,
                            current_incident_status=1,
                            current_incident_status_updated_at=temp_incident.current_incident_status_updated_at,
                            current_incident_x_axis=temp_incident.current_incident_x_axis,
                            current_incident_y_axis=temp_incident.current_incident_y_axis,
                            current_incident_notes=temp_incident.current_incident_notes,
                            branch_id=temp_incident.branch_id,
                        )
                        db.session.add(new_current_incident)
                        db.session.flush()

                        predefined_missions = IncidentTypeMission.query.filter_by(
                            incident_type_id=new_current_incident.current_incident_type_id
                        ).all()

                        if not predefined_missions:
                            raise Exception(
                                f"No predefined missions for incident type {new_current_incident.current_incident_type_id}")

                        for m in predefined_missions:
                            db.session.add(CurrentIncidentMission(
                                current_incident_id=new_current_incident.current_incident_id,
                                current_incident_mission_id=m.mission_id,
                                current_incident_mission_order=m.mission_order,
                                current_incident_mission_status=1,
                            ))

                        manager = assign_incident_manager(new_current_incident)
                        if not manager:
                            raise Exception("No available managers")

                        new_current_incident.manager_id = manager.user_id
                        db.session.add(CurrentIncidentManager(
                            current_incident_id=new_current_incident.current_incident_id,
                            user_id=manager.user_id,
                            assigned_by=1,
                            assigned_at=now
                        ))
                        db.session.add(CurrentIncidentStatusSeverityHistory(
                            current_incident_id=new_current_incident.current_incident_id,
                            current_incident_status=new_current_incident.current_incident_status,
                            current_incident_status_changed_by=1,
                            current_incident_status_changed_at=now,
                            current_incident_severity=new_current_incident.current_incident_severity,
                            current_incident_severity_changed_by=1,
                            current_incident_severity_changed_at=now
                        ))

                        temp_incident.processed = True
                        db.session.commit()
                        print(f"✅ Incident {new_current_incident.current_incident_id} committed successfully")

                        # snapshot everything needed before context closes
                        incident_dict = new_current_incident.to_dict()
                        device_tokens = [tok.token for tok in manager.tokens if tok.token and tok.token.strip()]
                        incident_id = str(new_current_incident.current_incident_id)
                        incident_desc = new_current_incident.current_incident_description

                    except Exception as processing_err:
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                        temp_incident.processed = None
                        db.session.commit()
                        print(f"❌ Incident processing failed: {processing_err}")
                        socketio.sleep(1)
                        continue  # ← skip notifications, go to next iteration

                    # --- Post-Commit Notifications (outside inner try, inside app_context) ---
                    try:
                        socketio.start_background_task(lambda d=incident_dict: socketio.emit("incident_created", d))

                        if device_tokens:
                            socketio.start_background_task(
                                dispatch_notification,
                                device_tokens,
                                "🚨 أزمة جديدة",
                                f"تم تعيينك مديراً لازمة {incident_desc}",
                                {"incident_id": incident_id, "type": "incident_created"}
                            )
                        print("🔔 Notification dispatched")

                    except Exception as notify_err:
                        print(f"⚠️ Notification failed: {notify_err}")

                else:
                    socketio.sleep(5)

        except Exception as outer_err:
            import traceback
            traceback.print_exc()
            print(f"💥 Outer error on iteration {iteration}: {outer_err}")
            socketio.sleep(5)


@app.route('/')
def home():  # put application's code here
    # print("test")
    return jsonify({"response": "بسم الله "})


if __name__ == '__main__':
    print('Flask-SocketIO async_mode:', socketio.async_mode)
    socketio.start_background_task(listen_to_temp_inserts)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True, use_reloader=False) #, use_reloader=False

