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
        nullable=False
    )

    current_incident_severity_updated_at = db.Column(
        db.DateTime,
        nullable=False
    )

    current_incident_status = db.Column(
        db.Integer,
        db.ForeignKey('incident_statuses.incident_status_id'),
        nullable=False
    )

    current_incident_status_updated_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=False
    )

    current_incident_status_updated_at = db.Column(
        db.DateTime,
        nullable=False
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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<IncidentSeverity id={self.severity_id} name={self.severity_name}>"


class IncidentStatus(db.Model):
    __tablename__ = 'incident_statuses'

    incident_status_id = db.Column(db.Integer, primary_key=True)

    incident_status_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return (
            f"<IncidentStatus id={self.incident_status_id} "
            f"name={self.incedent_status_name}>"
        )


