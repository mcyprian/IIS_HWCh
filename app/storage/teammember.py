from app import db


class TeamMember(db.Model):
    __tablename__ = 'teammembers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    surname = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    role = db.Column(db.String(64))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    type = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'teammember',
        'polymorphic_on': type
    }

    def __repr__(self):
        return '<TeamMember {}>'.format(self.name)


class Player(TeamMember):
    __tablename__ = 'players'
    id = db.Column(db.Integer, db.ForeignKey('teammembers.id'), primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(64), nullable=False)
    club = db.Column(db.String(64))
    events = db.relationship('Event', backref=db.backref('player'))

    __mapper_args__ = {
        'polymorphic_identity': 'player'
    }

    def __repr__(self):
        return '<Player {}>'.format(self.name)
