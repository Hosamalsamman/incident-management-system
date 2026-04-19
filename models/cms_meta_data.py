from datetime import datetime
from decimal import Decimal

from extensions import db
from sqlalchemy.dialects.mssql import NVARCHAR

class CurrentIncidentTemp(db.Model):
    __tablename__ = "current_incidents_Temp"

    cms_case_id = db.Column(db.Integer, primary_key=True)

    current_incident_description = db.Column(NVARCHAR(None), nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)
    current_incident_type_id = db.Column(db.Integer, nullable=False)

    current_incident_created_by = db.Column(db.Integer, nullable=False)
    current_incident_created_at = db.Column(db.DateTime, nullable=False)

    current_incident_severity = db.Column(db.Integer, nullable=False)
    current_incident_severity_updated_by = db.Column(db.Integer, nullable=True)
    current_incident_severity_updated_at = db.Column(db.DateTime, nullable=True)

    current_incident_status = db.Column(db.Integer, nullable=False)
    current_incident_status_updated_by = db.Column(db.Integer, nullable=True)
    current_incident_status_updated_at = db.Column(db.DateTime, nullable=True)

    current_incident_x_axis = db.Column(db.Numeric(8, 6), nullable=True)
    current_incident_y_axis = db.Column(db.Numeric(9, 6), nullable=True)

    current_incident_notes = db.Column(NVARCHAR(None), nullable=True)

    manager_id = db.Column(db.Integer, nullable=True)

    processed = db.Column(db.Boolean, nullable=True, default=False)

    operation = db.Column(db.String(50), nullable=True)

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
        return result