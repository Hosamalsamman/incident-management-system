from extensions import db

class Branch(db.Model):
    __tablename__ = 'branches'

    branch_id = db.Column(
        db.Integer,
        primary_key=True
    )

    branch_name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    incidents = db.relationship('CurrentIncident', back_populates='branch')
    branch_sectors = db.relationship('SectorBranch', back_populates='branch')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<Branch id={self.branch_id} name={self.branch_name}>"


class SectorManagement(db.Model):
    __tablename__ = "sectors_managements"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(400), nullable=False, unique=True)

    from_x_axis = db.Column(db.Numeric(8, 6), nullable=False)
    to_x_axis   = db.Column(db.Numeric(8, 6), nullable=False)
    from_y_axis = db.Column(db.Numeric(9, 6), nullable=False)
    to_y_axis   = db.Column(db.Numeric(9, 6), nullable=False)

    parent_sector_management_id = db.Column(
        db.Integer,
        db.ForeignKey("sectors_managements.id"),
        nullable=True
    )

    authority_level_id = db.Column(
        db.Integer,
        db.ForeignKey("authority_levels.id"),
        nullable=False
    )

    classifications = db.relationship(
        "SectorClassification",
        back_populates="sector_management")

    # 🔗 Self-reference (hierarchy)
    parent_sector = db.relationship(
        "SectorManagement",
        remote_side=[id],
        back_populates="child_sectors"
    )

    child_sectors = db.relationship(
        "SectorManagement",
        back_populates="parent_sector"
    )

    # 🔗 Authority level
    authority_level = db.relationship(
        "AuthorityLevel",
        back_populates="sectors"
    )

    # 🔁 Users assigned to this sector
    users = db.relationship(
        "User",
        back_populates="sector_management"
    )

    sector_branches = db.relationship("SectorBranch", back_populates="sector")


class SectorClassification(db.Model):
    __tablename__ = 'sector_classifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sector_management_id = db.Column(db.Integer, db.ForeignKey('sectors_managements.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classifications.class_id'), nullable=False)

    # Relationships
    sector_management = db.relationship("SectorManagement", back_populates="classifications")
    classification = db.relationship("Classification", back_populates="sector_classifications")

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('sector_management_id', 'class_id', name='uq_sector_classifications_complex'),
    )

    def to_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["sector_management"] = self.sector_management.to_dict()
        data["class"] = self.classification.to_dict()
        return data

    def __repr__(self):
        return f"<SectorClassification id={self.id}>"


class SectorBranch(db.Model):
    __tablename__ = 'sector_branches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sector_management_id = db.Column(db.Integer, db.ForeignKey('sectors_managements.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)

    # Relationships
    sector = db.relationship(
        "SectorManagement",
        back_populates="sector_branches"
    )

    branch = db.relationship(
        "Branch",
        back_populates="branch_sectors"
    )

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('sector_management_id', 'branch_id', name='uq_sector_branches_complex'),
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<SectorBranch id={self.id}>"