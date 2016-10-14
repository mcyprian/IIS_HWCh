from app import db


class PlayedIn(db.Model):
    __tablename__ = 'playedin'
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), primary_key=True)
    time = db.Column(db.Time)
    player = db.relationship("Player", backref='playedin')

    def __repr__(self):
        return '<PlayedIn {}, {}>'.format(self.player_id, self.formation_id)


class Formation(db.Model):  # TODO property get team home/away
    __tablename__ = 'formations'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    team_role = db.Column(db.String(64))
    playedins = db.relationship('PlayedIn', backref='formation')

    def __repr__(self):
        return '<Formation {}>'.format(self.id)
