from unittest.mock import patch

from models.current_incident_models import CurrentIncident, CurrentIncidentMission, CurrentIncidentStatusSeverityHistory
from models.incident_base_models import IncidentType, IncidentTypeMission, Classification, Mission
from models.sectors import Branch


def test_add_current_incident_success(app, client, auth_headers, db_session, mock_manager):
    with patch("routes.current_incidents.assign_incident_manager") as mock_assign, \
            patch("routes.current_incidents.dispatch_notification") as mock_dispatch, \
            patch("routes.current_incidents.socketio.start_background_task") as mock_background, \
            patch("routes.current_incidents.socketio.emit") as mock_emit:
        mock_assign.return_value = mock_manager
        classification = Classification(
            class_name="Utilities"
        )

        db_session.session.add(classification)
        db_session.session.flush()  # generate class_id
        incident_type = IncidentType(incident_type_name="Test Incident Type",
                                        classification=classification)

        branch = Branch(branch_name="Test Branch")

        db_session.session.add_all([
            incident_type,
            branch
        ])
        db_session.session.flush()
        mission_obj = Mission(
            mission_name="Notify Police",
            classification=classification
        )

        db_session.session.add(mission_obj)
        db_session.session.flush()

        mission = IncidentTypeMission(
            incident_type_id=incident_type.incident_type_id,
            mission_id=mission_obj.mission_id,
            mission_order=1
        )
        db_session.session.add(mission)
        db_session.session.commit()

        response = client.post(
            "/add-current-incident",
            headers=auth_headers,
            json={
                "current_incident_description": "pipe break",
                "address": "Main Street",
                "current_incident_type_id": incident_type.incident_type_id,
                "current_incident_severity": 2,
                "current_incident_x_axis": 31.2,
                "current_incident_y_axis": 30.1,
                "current_incident_notes": "Test",
                "branch_id": branch.branch_id
            }
        )
        with app.app_context():
            incident = CurrentIncident.query.first()
            missions = CurrentIncidentMission.query.filter_by(
                current_incident_id=incident.current_incident_id
            ).all()
            history = CurrentIncidentStatusSeverityHistory.query.filter_by(
                current_incident_id=incident.current_incident_id
            ).first()

        assert incident is not None
        assert incident.manager_id == 5
        assert incident.current_incident_description == "pipe break"
        assert len(missions) == 1
        assert history is not None
        assert response.status_code == 200
        data = response.get_json()
        print(response.status_code)
        print(response.get_json())
        assert "تم إضافة الأزمة بنجاح" in data["success"]

        mock_assign.assert_called_once()
        mock_background.assert_called_once()
        args = mock_background.call_args
        print(args)
        func = mock_background.call_args.args[0]
        func()
        mock_dispatch.assert_called_once()
        mock_emit.assert_called_once()
