from datetime import datetime
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

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.branch_id'),
        nullable=False
    )

    # Relationships
    missions = db.relationship("CurrentIncidentMission", back_populates="incident", lazy="joined")
    created_by_user = db.relationship(
        "User",
        foreign_keys=[current_incident_created_by],
        back_populates="created_incidents"
    )
    severity_updated_by_user = db.relationship(
        "User",
        foreign_keys=[current_incident_severity_updated_by],
        back_populates="severity_updated_incidents"
    )
    status_updated_by_user = db.relationship(
        "User",
        foreign_keys=[current_incident_status_updated_by],
        back_populates="status_updated_incidents"
    )
    incident_type = db.relationship("IncidentType", back_populates="incidents")
    severity = db.relationship("IncidentSeverity", back_populates="incidents")
    status = db.relationship("Status", back_populates="incidents")
    branch = db.relationship('Branch', back_populates='incidents')
    status_severity_history = db.relationship("CurrentIncidentStatusSeverityHistory", back_populates="current_incident")
    incident_managers = db.relationship("CurrentIncidentManager", back_populates="incident")

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                result[c.name] = val.isoformat()  # ✅ Convert to ISO string
            elif isinstance(val, Decimal):
                result[c.name] = float(val)
            else:
                result[c.name] = val
        result["branch_name"] = self.branch.branch_name
        result["user_name"] = self.created_by_user.emp_name
        result["incident_type_name"] = self.incident_type.incident_type_name
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
    status_updated_by_user = db.relationship(
        "User",
        foreign_keys=[current_incident_mission_status_updated_by],
        back_populates="mission_status_updated_missions"
    )
    status = db.relationship("Status", foreign_keys=[current_incident_mission_status])
    status_history = db.relationship(
        "CurrentIncidentMissionStatusHistory",
        back_populates="current_incident_mission",
        order_by="CurrentIncidentMissionStatusHistory.current_incident_mission_status_updated_at"
    )

    def to_dict(self):
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                result[c.name] = val.isoformat()  # ✅ Convert to ISO string
            elif isinstance(val, Decimal):
                result[c.name] = float(val)
            else:
                result[c.name] = val
        result["mission_name"] = self.mission.mission_name
        return result

    def __repr__(self):
        return (
            f"<CurrentIncidentMission incident_id={self.current_incident_id} "
            f"mission_id={self.current_incident_mission_id} "
            f"order={self.current_incident_mission_order}>"
        )


class CurrentIncidentStatusSeverityHistory(db.Model):
    __tablename__ = "current_incident_status_severity_history"

    current_incident_id = db.Column(
        db.Integer,
        db.ForeignKey("current_incidents.current_incident_id"),
        primary_key=True
    )

    current_incident_status = db.Column(
        db.Integer,
        db.ForeignKey("statuses.status_id"),
        nullable=False
    )

    current_incident_status_changed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    current_incident_status_changed_at = db.Column(
        db.DateTime,
        nullable=False
    )

    current_incident_severity = db.Column(
        db.Integer,
        db.ForeignKey("incident_severities.severity_id"),
        nullable=False
    )

    current_incident_severity_changed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    current_incident_severity_changed_at = db.Column(
        db.DateTime,
        nullable=False
    )

    # relationships
    current_incident = db.relationship(
        "CurrentIncident",
        back_populates="status_severity_history"
    )

    status = db.relationship("Status")
    severity = db.relationship("IncidentSeverity")

    status_changed_by = db.relationship(
        "User",
        foreign_keys=[current_incident_status_changed_by]
    )

    severity_changed_by = db.relationship(
        "User",
        foreign_keys=[current_incident_severity_changed_by]
    )

    def __repr__(self):
        return (
            f"<IncidentHistory incident={self.current_incident_id} "
            f"status={self.current_incident_status} "
            f"severity={self.current_incident_severity}>"
        )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CurrentIncidentMissionStatusHistory(db.Model):
    __tablename__ = "current_incident_mission_status_history"

    current_incident_mission_id = db.Column(
        db.Integer,
        db.ForeignKey("current_incident_missions.id"),
        primary_key=True
    )

    current_incident_mission_status = db.Column(
        db.Integer,
        db.ForeignKey("statuses.status_id"),
        nullable=False
    )

    current_incident_mission_status_updated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    current_incident_mission_status_updated_at = db.Column(
        db.DateTime,
        nullable=False
    )

    # relationships
    current_incident_mission = db.relationship(
        "CurrentIncidentMission",
        back_populates="status_history"
    )

    status = db.relationship("Status")

    updated_by = db.relationship(
        "User",
        foreign_keys=[current_incident_mission_status_updated_by]
    )

    def __repr__(self):
        return (
            f"<MissionStatusHistory mission={self.current_incident_mission_id} "
            f"status={self.current_incident_mission_status}>"
        )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CurrentIncidentManager(db.Model):
    __tablename__ = "current_incident_managers"

    id = db.Column(db.Integer, primary_key=True)

    current_incident_id = db.Column(
        db.Integer,
        db.ForeignKey("current_incidents.current_incident_id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    assigned_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # 🔗 Relationships
    incident = db.relationship(
        "CurrentIncident",
        back_populates="incident_managers"
    )

    manager = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="managed_incidents"
    )

    assigned_by_user = db.relationship(
        "User",
        foreign_keys=[assigned_by],
        back_populates="assignments_made"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "current_incident_id",
            "user_id",
            name="uq_current_incident_managers_complex"
        ),
    )