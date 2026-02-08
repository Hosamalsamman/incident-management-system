from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)

    emp_code = db.Column(
        db.String(8),
        db.ForeignKey('employees.emp_code'),
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    userpassword = db.Column(
        db.String(300),
        nullable=False
    )

    group_id = db.Column(
        db.Integer,
        db.ForeignKey('groups.group_id'),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        server_default='0'
    )


    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


    def __repr__(self):
        return f"<User id={self.user_id} username={self.username}>"


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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"<Group id={self.group_id} name={self.group_name}>"
