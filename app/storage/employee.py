from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)
    position = db.Column(db.String(64))
    events = db.relationship('Event', backref=db.backref('employee'))
    _password = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Attribute password is unreadable')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):  # TODO will be needed?
        return check_password_hash(self._password, password)

    def __repr__(self):
        return '<Employee {}>'.format(self.name)
