from app import db


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    time = db.Column(db.Date)
    information = db.Column(db.String(255))  # TODO: remove this?
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    teammember_id = db.Column(db.Integer, db.ForeignKey('teammembers.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    def __repr__(self):
        return '<Event {}>'.format(self.id)
