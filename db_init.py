import datetime

from app import db
from app.storage import *


def recreate_all():
    db.drop_all()
    db.create_all()


def fill_db():
    A = Group(code='A')
    svk = Team(name='Slovakia', code='SVK', max_members=30, group=A)
    rus = Team(name='Russia', code='RUS', max_members=30, group=A)

    zdeno = Player(name='Zdeno', surname='Chara', date_of_birth=datetime.date(1977, 3, 18),
                   role='player', number=33, position='defender', club='Boston Bruins', team=svk)

    alex = Player(name='Alex', surname='Ovechkin', date_of_birth=datetime.date(1985, 9, 17),
                  role='player', number=8, position='forward', club='Washington Capitals', team=rus)

    coach = TeamMember(name='Zdeno', surname='Ciger', date_of_birth=datetime.date(1969, 10, 19),
                       role='coach', team=svk)

    employee1 = Employee(name='Martin', surname='Novak', date_of_birth=datetime.date(1993, 11, 10),
                         position='event administrator', password='12345')

    match = Match(category='group', date=datetime.datetime(2016, 10, 3, 20, 0, 0), arena='Bratislava',
                  home_score=1, away_score=0, fans=10356, overtime=1, group=A, home_team_id=1, away_team_id=2)

    goal = Event(code='goal', time=datetime.datetime.now(), employee=employee1, player=zdeno,
                 match=match)

    ref1 = Referee(name='Vladimir', surname='Baluska', date_of_birth=datetime.date(1975, 1, 30))

    ref2 = Referee(name='Tomas', surname='Orlin', date_of_birth=datetime.date(1980, 5, 22))

    c1 = Controls(role='head')
    c1.referee = ref1
    match.controls.append(c1)

    c2 = Controls(role='line')
    c2.referee = ref2
    match.controls.append(c2)

    formation = Formation(team_role='home', match=match)

    p1 = PlayedIn(time=datetime.time(0, 12, 32))
    p1.player = zdeno
    formation.playedins.append(p1)

    db.session.add_all([svk, rus, zdeno, alex, coach, employee1, A, match, goal, ref1, ref2, c1,
                        c2, p1, formation])
