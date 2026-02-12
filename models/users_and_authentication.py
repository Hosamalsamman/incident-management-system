from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(8), nullable=False, unique=True)
    emp_name = db.Column(db.String(1000), nullable=False, unique=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    userpassword = db.Column(db.String(300), nullable=False)
    sector_management_id = db.Column(db.Integer, db.ForeignKey('sectors_managements.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=True)
    authority_level_id = db.Column(db.Integer, db.ForeignKey('authority_levels.id'), nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=False)

    # 🔗 Relationships
    group = db.relationship(
        'Group',
        back_populates='users'
    )
    # 🔁 Incidents CREATED by this user
    created_incidents = db.relationship(
        "CurrentIncident",
        foreign_keys="CurrentIncident.current_incident_created_by",
        back_populates="created_by_user"
    )
    # 🔁 Incidents where this user updated SEVERITY
    severity_updated_incidents = db.relationship(
        "CurrentIncident",
        foreign_keys="CurrentIncident.current_incident_severity_updated_by",
        back_populates="severity_updated_by_user"
    )
    # 🔁 Incidents where this user updated STATUS
    status_updated_incidents = db.relationship(
        "CurrentIncident",
        foreign_keys="CurrentIncident.current_incident_status_updated_by",
        back_populates="status_updated_by_user"
    )
    # 🔁 Missions where this user updated MISSION STATUS
    mission_status_updated_missions = db.relationship(
        "CurrentIncidentMission",
        foreign_keys="CurrentIncidentMission.current_incident_mission_status_updated_by",
        back_populates="status_updated_by_user"
    )
    # 🔗 Sector
    sector_management = db.relationship(
        "SectorManagement",
        back_populates="users"
    )
    # 🔗 Authority
    authority_level = db.relationship(
        "AuthorityLevel",
        back_populates="users"
    )
    # Incidents this user is assigned as manager
    managed_incidents = db.relationship(
        "CurrentIncidentManager",
        foreign_keys="CurrentIncidentManager.user_id",
        back_populates="manager"
    )
    # Assignments this user performed
    assignments_made = db.relationship(
        "CurrentIncidentManager",
        foreign_keys="CurrentIncidentManager.assigned_by",
        back_populates="assigned_by_user"
    )
    uploaded_incident_photos = db.relationship(
        "CurrentIncidentPhoto",
        back_populates="uploaded_by"
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<User id={self.user_id} name={self.emp_name}>"


class Group(db.Model):
    __tablename__ = 'groups'

    group_id = db.Column(db.Integer, primary_key=True)

    group_name = db.Column(
        db.String(400),
        nullable=False,
        unique=True
    )

    group_notification = db.Column(
        db.String(1000),
        nullable=True
    )

    users = db.relationship(
        'User',
        back_populates='group'
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<Group id={self.group_id} name={self.group_name}>"

class AuthorityLevel(db.Model):
    __tablename__ = "authority_levels"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False, unique=True)

    # 🔁 One authority level → many sectors
    sectors = db.relationship(
        "SectorManagement",
        back_populates="authority_level"
    )

    # 🔁 One authority level → many users
    users = db.relationship(
        "User",
        back_populates="authority_level"
    )


