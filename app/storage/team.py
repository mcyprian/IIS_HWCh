from app import db


class Team(db.Model):  # TODO property na vyhry, prehry, vyhry po predlzeni body ...
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    code = db.Column(db.String(3), nullable=False)
    max_members = (db.Column(db.Integer))

    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    members = db.relationship('TeamMember', backref=db.backref('team'))
    home_matches = db.relationship('Match', foreign_keys='Match.home_team_id')
    away_matches = db.relationship('Match', foreign_keys='Match.away_team_id')

    def __repr__(self):
        return '<Team {}>'.format(self.name)
