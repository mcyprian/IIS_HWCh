from app import db


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)
    position = db.Column(db.String(64))
    events = db.relationship('Event', backref=db.backref('employee'))

    def __repr__(self):
        return '<Employee {}>'.format(self.name)
