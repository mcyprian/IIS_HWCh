from app import db


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True, unique=True)
    code = db.Column(db.String(3), nullable=False, unique=True)
    max_members = (db.Column(db.Integer))

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    members = db.relationship('TeamMember', backref=db.backref('team'))
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id')
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id')
    events = db.relationship('Event', backref=db.backref('team'))

    def __repr__(self):
        return '<Team {}>'.format(self.name)
