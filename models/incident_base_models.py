from extensions import db

class IncidentType(db.Model):
    __tablename__ = 'incident_types'

    incident_type_id = db.Column(db.Integer, primary_key=True)
    incident_type_name = db.Column(db.String(300), nullable=False, unique=True)

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classifications.class_id'),
        nullable=False
    )

    classification = db.relationship('Classification', back_populates='incident_types')
    incidents = db.relationship("CurrentIncident", back_populates="incident_type")

    missions = db.relationship(
        'IncidentTypeMission',
        back_populates='incident_type'
    )

    def __repr__(self):
        return f"<IncidentType {self.incident_type_name}>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["class_name"] = self.classification.class_name
        data["missions"] = [mission.to_dict() for mission in self.missions]
        return data


class Mission(db.Model):
    __tablename__ = 'missions'

    mission_id = db.Column(db.Integer, primary_key=True)
    mission_name = db.Column(db.String(4000), nullable=False, unique=True)

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classifications.class_id'),
        nullable=False
    )

    incident_types = db.relationship(
        'IncidentTypeMission',
        back_populates='mission'
    )

    classification = db.relationship('Classification', back_populates='missions')

    def __repr__(self):
        return f"<Mission {self.mission_name}>"

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["class_name"] = self.classification.class_name
        return data


class Classification(db.Model):
    __tablename__ = 'classifications'

    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(255), nullable=False)

    missions = db.relationship('Mission', back_populates='classification')
    incident_types = db.relationship('IncidentType', back_populates='classification')
    sector_classifications = db.relationship(
        "SectorClassification",
        back_populates="classification"
    )

    def __repr__(self):
        return f"<Classification {self.class_name}>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class IncidentTypeMission(db.Model):
    __tablename__ = 'incident_type_missions'

    incident_type_id = db.Column(
        db.Integer,
        db.ForeignKey('incident_types.incident_type_id'),
        primary_key=True
    )
    mission_id = db.Column(
        db.Integer,
        db.ForeignKey('missions.mission_id'),
        primary_key=True
    )
    mission_order = db.Column(db.Integer, nullable=False, primary_key=True)

    incident_type = db.relationship('IncidentType', back_populates='missions')
    mission = db.relationship('Mission', back_populates='incident_types')

    def __repr__(self):
        return (
            f"<IncidentTypeMission incident_type_id={self.incident_type_id} "
            f"mission_id={self.mission_id} order={self.mission_order}>"
        )

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["mission_name"] = self.mission.mission_name
        data["mission_class_name"] = self.mission.classification.class_name
        return data
