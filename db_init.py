import datetime
from random import randrange, sample
from faker import Factory
from itertools import combinations

from app import db
from app.storage import *
from app.settings import START_DAY
from app.roles import roles


def fake_name(fake):
    return fake.first_name_male()


def fake_surname(fake):
    return fake.last_name_male()


def fake_date(fake):
    return fake.date_time_between(start_date='-38y', end_date='-18y').date()


def fake_num():
    return randrange(1, 99)


def fake_club(fake):
    return fake.city()


def recreate_all():
    db.drop_all()
    db.create_all()


def add_row(obj, rows):
    rows.append(obj)
    return obj


def fill_db():
    rows = []

    # Add teams data
    A = add_row(Group(code='A'), rows)
    B = add_row(Group(code='B'), rows)

    svk = add_row(Team(name='Slovakia',
                       code='SVK',
                       max_members=30,
                       group=A),
                  rows)
    rus = add_row(Team(name='Russia',
                       code='RUS',
                       max_members=30,
                       group=A),
                  rows)
    cze = add_row(Team(name='Czech Republic',
                       code='CZE',
                       max_members=30,
                       group=A),
                  rows)
    swe = add_row(Team(name='Sweden',
                       code='SWE',
                       max_members=30,
                       group=A),
                  rows)
    fin = add_row(Team(name='Finland',
                       code='FIN',
                       max_members=30,
                       group=B),
                  rows)
    usa = add_row(Team(name='USA', code='USA', max_members=30, group=B), rows)
    can = add_row(Team(name='Canada',
                       code='CAN',
                       max_members=30,
                       group=B),
                  rows)
    ger = add_row(Team(name='Germany', code='GER',
                       max_members=30,
                       group=B),
                  rows)

    # Add players and couches data
    players = {}
    for team_obj, locale in (
            (svk, 'cs_CZ'),
            (rus, 'ru_RU'),
            (cze, 'cs_CZ'),
            (swe, 'sv_SE'),
            (fin, 'fi_FI'),
            (usa, 'EN_us'),
            (can, 'en_CA'),
            (ger, 'de_DE')):
        players[team_obj] = []
        fake = Factory.create(locale)
        for p in range(27):
            if p < 3:
                position = 'goalie'
            else:
                position = 'forward' if p < 16 else 'defender'
            players[team_obj].append(
                add_row(Player(name=fake_name(fake),
                               surname=fake_surname(fake),
                               date_of_birth=fake_date(fake),
                               role='player',
                               number=fake_num(),
                               position=position,
                               club=fake_club(fake),
                               team=team_obj),
                        rows))

        add_row(TeamMember(name=fake_name(fake),
                           surname=fake_surname(fake),
                           date_of_birth=fake_date(fake),
                           role='assistant',
                           team=team_obj),
                rows)

        add_row(TeamMember(name=fake_name(fake),
                           surname=fake_surname(fake),
                           date_of_birth=fake_date(fake),
                           role='assistant',
                           team=team_obj),
                rows)

        add_row(
            TeamMember(name=fake_name(fake), surname=fake_surname(fake),
                       date_of_birth=fake_date(fake),
                       role='coach',
                       team=team_obj),
         rows)

    # Add employees data
    fake = Factory.create('en_US')
    add_row(Employee(name=fake.first_name(), surname=fake.last_name(),
                     login='admin', date_of_birth=fake_date(fake),
                     role=roles['ADMINISTRATOR'],
                     password='12345'), rows)

    add_row(Employee(name=fake.first_name(), surname=fake.last_name(),
                     login='manager', date_of_birth=fake_date(fake),
                     role=roles['MANAGER'],
                     password='12345'), rows)

    add_row(Employee(name=fake.first_name(), surname=fake.last_name(),
                     login='employee', date_of_birth=fake_date(fake),
                     role=roles['EMPLOYEE'],
                     password='12345'), rows)

    employees = []
    for e in range(10):
        name = fake.first_name()
        surname = fake.last_name()
        login = name[0].lower() + surname.lower()
        employees.append(add_row(Employee(name=name,
                                          surname=surname,
                                          login=login,
                                          date_of_birth=fake_date(fake),
                                          role=roles['EMPLOYEE'],
                                          password='12345'),
                                 rows))

    # Add referees data
    referees = []
    for r in range(10):
        referees.append(add_row(Referee(name=fake_name(fake),
                                        surname=fake_surname(fake),
                                        date_of_birth=fake_date(fake)),
                                rows))

    values = [x & 1 for x in range(22)]
    vs = [list(combinations([svk, rus, cze, swe], 2)),
          list(combinations([fin, usa, can, ger], 2))]

    # Add matches data
    matches = []
    match_date = START_DAY - datetime.timedelta(days=1)
    for m in range(22):
        employee = employees[randrange(len(employees))]
        if m & 1:
            match_date = match_date.replace(hour=20)
        else:
            match_date = match_date.replace(hour=16)
            match_date += datetime.timedelta(1)

        if m < 12:
            sel_teams = vs[m & 1][randrange(len(vs[m & 1]))]
            vs[m & 1].remove(sel_teams)
            group = sel_teams[0].group
            arena = 'Bratislava' if group == A else 'Kosice'
        else:
            sel_teams = [None, None]
            group = None
            arena = 'Bratislava' if values[m] else 'Kosice'

        matches.append(add_row(Match(category='group', datetime=match_date,
                                     arena=arena,
                                     fans=randrange(3000, 18000),
                                     group=group,
                                     home_team=sel_teams[0],
                                     away_team=sel_teams[1]), rows))

        matches[m].overtime = 0

        # Add referees
        picked_refs = sample(referees, 4)
        c1 = add_row(Controls(role='head'), rows)
        c1.referee = picked_refs[0]
        matches[m].controls.append(c1)

        c2 = add_row(Controls(role='line'), rows)
        c2.referee = picked_refs[1]
        matches[m].controls.append(c2)

        c3 = add_row(Controls(role='line'), rows)
        c3.referee = picked_refs[2]
        matches[m].controls.append(c3)

        c4 = add_row(Controls(role='video'), rows)
        c4.referee = picked_refs[3]
        matches[m].controls.append(c4)

        if m >= 7:
            for id_str, team in zip(['home', 'away'], sel_teams):
                for f in range(5):
                    formation = add_row(Formation(
                        team_role=id_str, match=matches[-1]), rows)
        else:
            # Formations
            participants = {}
            for id_str, team in zip(['home', 'away'], sel_teams):
                goalies = sample(players[team][:3], 2)  # golies
                forwards = sample(players[team][3:16], 12)  # forwards
                defenders = sample(players[team][16:], 8)  # defenders
                player_range = goalies + forwards + defenders
                participants[team] = [p for p in player_range]

                formation = add_row(Formation(
                    team_role=id_str, match=matches[-1]),
                    rows)
                g = add_row(PlayedIn(time=datetime.timedelta(
                    minutes=60, seconds=0), role='goalie'),
                    rows)
                g.player = goalies.pop()
                formation.playedins.append(g)

                for f in range(4):
                    formation = add_row(
                        Formation(team_role=id_str,
                                  match=matches
                                  [-1]),
                                        rows)
                    for n in range(3):
                        p1 = add_row(PlayedIn(time=datetime.timedelta(
                            minutes=randrange(5, 20), seconds=randrange(60)),
                            role='forward'), rows)
                        p1.player = forwards.pop()
                        formation.playedins.append(p1)
                    for n in range(2):
                        p1 = add_row(PlayedIn(time=datetime.timedelta(
                            minutes=randrange(5, 20), seconds=randrange(60)),
                            role='defender'), rows)
                        p1.player = defenders.pop()
                        formation.playedins.append(p1)

            home_score = 0
            away_score = 0
            events = ['shot', 'offside', 'interference']
            for e in range(randrange(50, 110)):
                team = sel_teams[randrange(2)]
                event_type = events[randrange(len(events))]
                event_time = datetime.timedelta(minutes=randrange(60),
                                                seconds=randrange(60))
                picked_player = participants[team][
                    randrange(len(participants[team]))]
                add_row(Event(code=event_type, time=event_time,
                              employee=employee, player=picked_player,
                              match=matches[-1], team=team),
                        rows)

            events = ['goal', 'penalty']
            for e in range(randrange(5, 12)):
                team = sel_teams[randrange(2)]
                event_type = events[randrange(len(events))]
                event_time = datetime.timedelta(minutes=randrange(60),
                                                seconds=randrange(60))
                # pick participants
                picked_players = sample(participants[team][2:], 3)
                if event_type == 'goal':
                    if team == sel_teams[0]:
                        home_score += 1
                    else:
                        away_score += 1
                    add_row(Event(code='assist', time=event_time,
                                  employee=employee, player=picked_players[1],
                                  match=matches[-1],
                                  team=team),
                            rows)
                    add_row(Event(code='assist', time=event_time,
                                  employee=employee, player=picked_players[2],
                                  match=matches[-1],
                                  team=team),
                            rows)
                    add_row(Event(code='shot', time=event_time,
                                  employee=employee, player=picked_players[0],
                                  match=matches[-1], team=team),
                            rows)
                add_row(Event(code=event_type, time=event_time,
                              employee=employee, player=picked_players[0],
                              match=matches[-1], team=team),
                        rows)

            if home_score == away_score:
                matches[m].overtime = randrange(1, 3)
                event_time = datetime.timedelta(minutes=randrange(60),
                                                seconds=randrange(60))
                team = sel_teams[randrange(2)]
                picked_players = sample(participants[team], 3)
                add_row(
                    Event(code='assist', time=event_time, employee=employee,
                          player=picked_players[1], match=matches[-1],
                          team=team), rows)
                add_row(
                    Event(code='assist', time=event_time, employee=employee,
                          player=picked_players[2], match=matches[-1],
                          team=team), rows)
                add_row(Event(code='shot', time=event_time, employee=employee,
                              player=picked_players[0], match=matches[-1],
                              team=team), rows)
                add_row(Event(code='goal', time=event_time, employee=employee,
                              player=picked_players[0], match=matches[-1],
                              team=team), rows)

    db.session.add_all(rows)
