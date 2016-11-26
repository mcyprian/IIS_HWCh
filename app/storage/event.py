from app import db


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False)
    time = db.Column(db.Interval, nullable=False, index=True)
    information = db.Column(db.String(255))  # TODO: remove this?
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    teammember_id = db.Column(db.Integer, db.ForeignKey('teammembers.id'), nullable=False,
                              index=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True, index=True)

    def __repr__(self):
        return '<Event {}>'.format(self.id)
