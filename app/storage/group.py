from app import db


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(1))
    teams = db.relationship('Team', backref=db.backref('group'))
    matches = db.relationship('Match', backref=db.backref('group'))

    def __repr__(self):
        return '<Group {}>'.format(self.code)
