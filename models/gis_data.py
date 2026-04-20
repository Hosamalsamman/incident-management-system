from extensions import db

class ValveType(db.Model):
    __tablename__ = "valve_types"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(300), nullable=False)
    name_en = db.Column(db.String(300), nullable=False)
    abbreviation = db.Column(db.String(50), nullable=False)

    # relationship (read-only usage)
    valves = db.relationship(
        "Valve", back_populates="valve_type")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<Valve id={self.id} name_ar={self.name_ar} name_en={self.name_en} abbrev={self.abbreviation}>"


class Valve(db.Model):
    __tablename__ = "valves"

    id = db.Column(db.Integer, primary_key=True)

    valve_type_id = db.Column(
        db.Integer,
        db.ForeignKey("valve_types.id"),
        nullable=False
    )

    position = db.Column(db.String(100), nullable=False)
    depth = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(200), nullable=False)

    diameter = db.Column(db.Integer, nullable=False)
    pipe_diameter = db.Column(db.Integer, nullable=False)

    direction = db.Column(db.String(100), nullable=False)
    num_of_tur = db.Column(db.Integer, nullable=False)
    In_Service_Year = db.Column(db.Integer, nullable=False)

    lat = db.Column(db.Numeric(9, 6), nullable=False)
    long = db.Column(db.Numeric(8, 6), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)

    valve_type = db.relationship(
        "ValveType",
        back_populates="valves",
        lazy="joined"   # 🔥 important for map (avoid N+1)
    )

    branch = db.relationship(
        "Branch",
        back_populates="valves"
    )

    def to_dict(self):
        return {
            "id": self.id,
            # "valve_type": self.valve_type.name_en if self.valve_type else None,
            "valve_type_id": self.valve_type_id,
            "valve_type": self.valve_type.to_dict(),
            "position": self.position,
            "depth": float(self.depth),
            "status": self.status,

            "diameter": self.diameter,
            "pipe_diameter": self.pipe_diameter,

            "direction": self.direction,
            "num_of_turns": self.num_of_tur,
            "in_service_year": self.In_Service_Year,

            "lat": float(self.lat),
            "long": float(self.long)
        }