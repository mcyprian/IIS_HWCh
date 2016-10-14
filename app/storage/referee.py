from app import db


class Controls(db.Model):
    __tablename__ = 'controls'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)
    referee_id = db.Column(db.Integer, db.ForeignKey('referees.id'), primary_key=True)
    role = db.Column(db.String(64))
    referee = db.relationship("Referee", backref='controls')

    def __repr__(self):
        return '<Controls {}, {}>'.format(self.match_id, self.referee_id)


class Referee(db.Model):
    __tablename__ = 'referees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    date_of_birth = db.Column(db.Date)

    def __repr__(self):
        return '<Referee {}>'.format(self.name)
