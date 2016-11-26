import datetime
from sqlalchemy import func, desc, or_

from app import db, login_manager
from app.storage import (Player,
                         Team,
                         Match,
                         Event,
                         Employee,
                         Formation,
                         PlayedIn,
                         TeamMember)
from app.settings import START_DAY


@login_manager.user_loader
def load_employee(employee_id):
    return db.session.query(Employee).get(int(employee_id))


def get_all_arenas(db):
    """Return list of all arenas."""
    return [i[0] for i in (db.session.query(Match.arena.distinct())
                           .all())]


def get_match_by_id(db, match_id):
    """Return selected match."""
    return (db.session.query(Match)
                      .filter_by(id=match_id)
                      .first())


def get_matches_by_day(db, day_num):
    """Return all matches scheduled for day day_num of the tournament."""
    match_date = START_DAY + datetime.timedelta(day_num - 1)
    next_day = (match_date + datetime.timedelta(1)).replace(hour=0, minute=0)
    return (db.session.query(Match)
                      .filter(Match.datetime >= match_date)
                      .filter(Match.datetime < next_day)
                      .all())


def get_matches_for_arena_by_day(db, arena, day_num):
    """Return all matches scheduled for day day_num inspecific arena."""
    match_date = START_DAY + datetime.timedelta(day_num - 1)
    next_day = (match_date + datetime.timedelta(1)).replace(hour=0, minute=0)
    return (db.session.query(Match)
                      .filter_by(arena=arena)
                      .filter(Match.datetime >= match_date)
                      .filter(Match.datetime < next_day)
                      .all())


def get_all_players(db):
    """Returns list of all players."""
    return (db.session.query(Player)
            .all())


def get_player_by_surname(db, player_surname):
    """Return list of Player objects matching surname regex."""
    return (db.session.query(Player)
                      .filter_by(surname=player_surname)
                      .all())


def get_player_by_surname_regex(db, player_surname):
    """Return list of Player objects matching surname regex."""
    return (db.session.query(Player)
                      .filter(Player.surname.like('%' + player_surname + '%'))
                      .all())


def get_player_by_id(db, player_id):
    """Return object of Player or None if not present."""
    return (db.session.query(Player)
                      .filter_by(id=player_id)
                      .first())


def get_player_rand(db):
    """Return random player."""
    return (db.session.query(Player)
                      .order_by(func.random())
                      .first())


def get_teams(db):
    """Return list of all Teams."""
    return (db.session.query(Team)
                      .all())


def get_team_by_name(db, team_name):
    """Return first Team object matching team_name."""
    return (db.session.query(Team)
                      .filter_by(name=team_name)
                      .first())


def get_team_rand(db):
    """Return random team."""
    return (db.session.query(Team)
                      .order_by(func.random())
                      .first())


def get_members_of_team_by_name(db, team_name, role='player'):
    """Return all players of team."""
    t = get_team_by_name(db, team_name)
    if t is not None:
        return (db.session.query(TeamMember)
                          .filter_by(team=t)
                          .filter_by(role=role)
                          .all())
    return None


def get_members_of_team(db, team, role='player'):
    """Return all players of team."""
    return (db.session.query(TeamMember)
            .filter_by(team=team)
            .filter_by(role=role)
            .all())


def get_score(db, m, home=True):
    """Return score of home team in match m if home is true,
    score of away team otherwise."""
    attr = 'home_team' if home else 'away_team'
    return (db.session.query(Event)
                      .filter_by(match=m)
                      .filter_by(team=getattr(m, attr))
                      .filter_by(code='goal')
                      .count())


def get_score_or_none(db, m, home=True):
    """Return score of home team in match m if home is true,
    score of away team otherwise. Return None if match not
    finished."""
    attr = 'home_team' if home else 'away_team'
    if not (db.session.query(Event)
                      .filter_by(match=m)
                      .all()):
        return None
    return (db.session.query(Event)
                      .filter_by(match=m)
                      .filter_by(team=getattr(m, attr))
                      .filter_by(code='goal')
                      .count())


def get_most_productive(db):
    """Return ordered list of the most productive players."""
    return (db.session.query(Player, func.count(Player.events))
                      .join(Event)
                      .filter(or_(Event.code == 'goal',
                                  Event.code == 'assist'))
                      .group_by(Player)
                      .order_by(desc(func.count(Player.events)))
                      .all())


def get_mvp(db, team):
    """Return ordered list of the most productive players."""
    mvp = (db.session.query(Player, func.count(Player.events))
                     .join(Event)
                     .filter(Player.team == team)
                     .filter(or_(Event.code == 'goal',
                                 Event.code == 'assist'))
                     .group_by(Player)
                     .order_by(desc(func.count(Player.events)))
                     .first())
    if mvp is None:
        first = (db.session.query(Player)
                           .filter_by(team=team)
                           .first())
    return mvp or (first, 0)


def get_num_of(db, player, what):
    """Return number of events of type what for selected player."""
    return (db.session.query(Event)
                      .filter_by(code=what)
                      .filter_by(player=player)
                      .count())


def get_total_time(db, player):
    """Return total time spent on ice in seconds."""
    query = (db.session.query(PlayedIn.time)
                       .filter_by(player=player)
                       .all())

    total = datetime.timedelta()
    for t in query:
        total += t[0]
    return total.seconds


def get_num_of_games(db, player):
    """Return number of games selected player participated in."""
    return (db.session.query(Formation)
                      .join(PlayedIn)
                      .filter(PlayedIn.player == player)
                      .distinct(Formation.match_id)
                      .count())


def get_matches_for_team(db, team, overtime=0):
    """Return all matches the team participates in."""
    return (db.session.query(Match)
                      .filter(or_(Match.home_team == team,
                                  Match.away_team == team))
                      .filter_by(overtime=overtime)
            .all())


def get_wins(db, team, overtime=0):
    "Return number of matches won by team"
    num = 0
    for m in get_matches_for_team(db, team, overtime):
        if m.home_team == team:
            if get_score(db, m, home=True) > get_score(db, m, home=False):
                num += 1
        else:
            if get_score(db, m, home=True) < get_score(db, m, home=False):
                num += 1
    return num


def get_losses(db, team, overtime=0):
    "Return number of matches won by team"
    num = 0
    for m in get_matches_for_team(db, team, overtime):
        if m.home_team == team:
            if get_score(db, m, home=True) < get_score(db, m, home=False):
                num += 1
        else:
            if get_score(db, m, home=True) > get_score(db, m, home=False):
                num += 1
    return num


def get_num_of_scored(db, team):
    "Return number of goals scored by team"
    return (db.session.query(Event)
                      .filter_by(code='goal')
                      .filter_by(team=team)
                      .count())


def get_num_of_received(db, team):
    "Return number of goals received by team"
    received = 0
    matches_query = (db.session.query(Match)
                     .filter(or_(Match.home_team == team,
                                 Match.away_team == team))
                     .all())

    for m in matches_query:
        home = False if m.home_team == team else True
        received += get_score(db, m, home=home)

    return received


def get_employee(db, login):
    """Return selected employee."""
    return (db.session.query(Employee)
                      .filter_by(login=login)
                      .first())


def get_all_employees(db):
    """Return list of all employees."""
    return (db.session.query(Employee)
                      .order_by(Employee.login)
                      .all())


def get_event(db, event_id):
    """Return selsected event."""
    return (db.session.query(Event)
                      .filter_by(id=event_id)
                      .first())


def get_events_of_match(db, match_id):
    """Return list of events for selected match."""
    return (db.session.query(Event)
                      .filter_by(match_id=match_id)
                      .order_by(Event.time)
                      .all())
