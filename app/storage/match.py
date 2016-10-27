from app import db


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date)
    arena = db.Column(db.String(64))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    fans = db.Column(db.Integer)
    overtime = db.Column(db.Integer)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    home_team = db.relationship('Team', foreign_keys=home_team_id,
                                backref='home_teams')
    away_team = db.relationship('Team', foreign_keys=away_team_id,
                                backref='away_teams')
    events = db.relationship('Event', backref=db.backref('match'))
    formations = db.relationship('Formation', backref=db.backref('match'))
    controls = db.relationship('Controls', backref='match')

    def __repr__(self):
        return '<Match {}>'.format(self.id)
