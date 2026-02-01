from decimal import Decimal

from extensions import db


class CurrentIncident(db.Model):
    __tablename__ = 'current_incidents'

    current_incident_id = db.Column(db.Integer, primary_key=True)

    current_incident_description = db.Column(
        db.String(4000),
        nullable=False
    )

    current_incident_type_id = db.Column(
        db.Integer,
        db.ForeignKey('incident_types.incident_type_id'),
        nullable=False
    )

    current_incident_created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=False
    )

    current_incident_created_at = db.Column(
        db.DateTime,
        nullable=False
    )

    current_incident_severity = db.Column(
        db.Integer,
        db.ForeignKey('incident_severities.severity_id'),
        nullable=False
    )

    current_incident_severity_updated_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=True
    )

    current_incident_severity_updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    current_incident_status = db.Column(
        db.Integer,
        db.ForeignKey('statuses.status_id'),
        nullable=False
    )

    current_incident_status_updated_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=True
    )

    current_incident_status_updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    current_incident_x_axis = db.Column(
        db.Numeric(8, 6),
        nullable=False
    )

    current_incident_y_axis = db.Column(
        db.Numeric(9, 6),
        nullable=False
    )

    current_incident_notes = db.Column(
        db.String(4000),
        nullable=True
    )

    # Relationships
    missions = db.relationship("CurrentIncidentMission", back_populates="incident", lazy="joined")
    created_by_user = db.relationship("User", foreign_keys=[current_incident_created_by])
    severity_updated_by_user = db.relationship("User", foreign_keys=[current_incident_severity_updated_by])
    status_updated_by_user = db.relationship("User", foreign_keys=[current_incident_status_updated_by])
    incident_type = db.relationship("IncidentType", back_populates="incidents")
    severity = db.relationship("IncidentSeverity", back_populates="incidents")
    status = db.relationship("Status", back_populates="incidents")

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)

            # Convert datetime to ISO string
            if isinstance(val, (db.DateTime().python_type,)):
                result[c.name] = val.isoformat()

            # Convert Decimal to float
            elif isinstance(val, Decimal):
                result[c.name] = float(val)

            # Everything else is fine
            else:
                result[c.name] = val

        result['missions'] = [m.to_dict() for m in self.missions]

        return result


    def __repr__(self):
        return (
            f"<CurrentIncident id={self.current_incident_id} "
            f"status={self.current_incident_status} "
            f"severity={self.current_incident_severity}>"
        )


class IncidentSeverity(db.Model):
    __tablename__ = 'incident_severities'

    severity_id = db.Column(db.Integer, primary_key=True)

    severity_name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    incidents = db.relationship("CurrentIncident", back_populates="severity")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<IncidentSeverity id={self.severity_id} name={self.severity_name}>"


class Status(db.Model):
    __tablename__ = 'statuses'

    status_id = db.Column(db.Integer, primary_key=True)

    status_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    incidents = db.relationship("CurrentIncident", back_populates="status")
    incident_missions = db.relationship("CurrentIncidentMission", back_populates="status")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return (
            f"<IncidentStatus id={self.status_id} "
            f"name={self.status_name}>"
        )


class CurrentIncidentMission(db.Model):
    __tablename__ = 'current_incident_missions'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    current_incident_id = db.Column(
        db.Integer,
        db.ForeignKey('current_incidents.current_incident_id'),
        unique=True,
        nullable=False
    )

    current_incident_mission_id = db.Column(
        db.Integer,
        db.ForeignKey('missions.mission_id'),
        unique=True,
        nullable=False
    )

    current_incident_mission_order = db.Column(
        db.Integer,
        unique=True,
        nullable=False
    )

    current_incident_mission_status = db.Column(
        db.Integer,
        db.ForeignKey('statuses.status_id'),
        nullable=False
    )

    current_incident_mission_status_updated_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=True
    )

    current_incident_mission_status_updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # Relationships
    incident = db.relationship("CurrentIncident", back_populates="missions")
    mission = db.relationship("Mission")
    status_updated_by_user = db.relationship("User", foreign_keys=[current_incident_mission_status_updated_by])
    status = db.relationship("Status", foreign_keys=[current_incident_mission_status])

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return (
            f"<CurrentIncidentMission incident_id={self.current_incident_id} "
            f"mission_id={self.current_incident_mission_id} "
            f"order={self.current_incident_mission_order}>"
        )
