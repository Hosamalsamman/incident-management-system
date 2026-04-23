from flask import jsonify
from routes import create_app
from extensions import socketio
from routes.common import send_to_group, dispatch_notification
from waitress import serve

app = create_app()


def listen_to_temp_inserts():
    from datetime import datetime
    from extensions import socketio, db
    from models.cms_meta_data import CurrentIncidentTemp
    from models.current_incident_models import CurrentIncident, CurrentIncidentMission, CurrentIncidentManager, \
        CurrentIncidentStatusSeverityHistory
    from models.incident_base_models import IncidentTypeMission
    from routes.common import add_tokens_to_group, commit_trial
    from routes.current_incidents import assign_incident_manager

    with app.app_context():
        # print("Starting DB Listener Background Task...")
        iteration = 0
        while True:
            iteration += 1
            # print(f"🔄 Loop iteration {iteration}")
            try:
                # Query for a new incident
                temp_incident = CurrentIncidentTemp.query.filter(
                    CurrentIncidentTemp.processed == False
                ).first()

                if temp_incident:
                    print(f"📥 Found incident {temp_incident.cms_case_id}, processing...")
                    # Mark as in-progress so it won't be picked up again
                    temp_incident.processed = None
                    db.session.commit()

                    try:
                        now = datetime.now()
                        new_current_incident = CurrentIncident(
                            current_incident_description=temp_incident.current_incident_description,
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

                        # Mark as processed successfully
                        temp_incident.processed = True
                        db.session.commit()

                        print(f"✅ Incident {new_current_incident.current_incident_id} committed successfully")

                        # --- Post-Commit Actions (Notifications) ---
                        try:
                            # print("📡 About to emit incident_created...")
                            incident_dict = new_current_incident.to_dict()
                            socketio.start_background_task(lambda d=incident_dict: socketio.emit("incident_created", d))
                            # print("📡 Emit done")

                            # print("🔔 Getting device tokens...")
                            device_tokens = [tok.token for tok in manager.tokens if tok.token]
                            print(f"🔔 Found {len(device_tokens)} tokens")
                            if device_tokens:
                                add_tokens_to_group(
                                    device_tokens,
                                    f"Team_incident_{new_current_incident.current_incident_id}"
                                )
                                # print("🔔 Tokens added to group")

                            # print("🔔 Sending notification...")

                            socketio.start_background_task(
                                lambda: dispatch_notification(
                                    topic=f"Team_incident_{new_current_incident.current_incident_id}",
                                    title="🚨 أزمة جديدة",
                                    body=f"تم تعيينك مديراً لازمة {new_current_incident.current_incident_description}",
                                    data={"incident_id": str(new_current_incident.current_incident_id),
                                          "type": "incident_created"}
                                )
                            )
                            print("🔔 Notification dispatched")

                        except Exception as notify_err:
                            import traceback
                            traceback.print_exc()
                            print(f"⚠️ Notification failed: {notify_err}")

                        print("✔️ Exiting if temp_incident block")
                        # Small sleep to prevent tight looping (CPU exhaustion) and allow cleanup
                        # socketio.sleep(3)

                    except Exception as processing_err:
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                        temp_incident.processed = None  # Failed permanently
                        db.session.commit()
                        print(f"❌ Incident processing failed, marked as failed: {processing_err}")
                        socketio.sleep(1)

                else:
                    # No incidents found, wait longer
                    # print(f"😴 No incidents, sleeping...")
                    socketio.sleep(5)

            except Exception as outer_err:
                import traceback
                traceback.print_exc()
                print(f"💥 Outer error on iteration {iteration}: {outer_err}")

                try:
                    db.session.rollback()
                except:
                    pass

                socketio.sleep(5)

            finally:
                # CRITICAL: Ensure session is cleaned up at the end of EVERY iteration
                # This prevents connection pool exhaustion
                try:
                    db.session.remove()
                    # print(f"🔁 Bottom of loop, iteration {iteration} complete")  # ← add this OUTSIDE finally
                except:
                    pass
            # print(f"🔁 Bottom of loop, iteration {iteration} complete")


@app.route('/')
def home():  # put application's code here
    # print("test")
    return jsonify({"response": "بسم الله "})


if __name__ == '__main__':
    print('Flask-SocketIO async_mode:', socketio.async_mode)
    socketio.start_background_task(listen_to_temp_inserts)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True, use_reloader=False) #, use_reloader=False

