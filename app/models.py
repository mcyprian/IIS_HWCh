from app import db


class TeamMember(db.Model):
    __tablename__ = 'teammembers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    role = db.Column(db.String(255))
    number = db.Column(db.Integer)
    position = db.Column(db.String(255))
    club = db.Column(db.String(255))
    team = db.Column(db.String(255))

    def __init__(self, name, surname, date, role, num, pos, club, team):
        self.name = name
        self.surname = surname
        self.date_of_birth = date
        self.role = role
        self.number = num
        self.position = pos
        self.club = club
        self.team = team

    def __repr__(self):
        return '<TeamMember {}>'.format(self.name)
