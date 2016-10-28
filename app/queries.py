import datetime

from app import db
from app.storage import Player, Team, Match
from app.settings import START_DAY


def get_player_by_surname(db, player_surname):
    """Return list of Player objects matching surname regex."""
    return (db.session.query(Player)
                      .filter_by(surname=player_surname)
                      .first())


def get_player_by_surname_regex(db, player_surname):
    """Return list of Player objects matching surname regex."""
    return (db.session.query(Player)
                      .filter(Player.surname.like('%' + player_surname + '%'))
                      .all())


def get_teams(db):
    """Return list of all Teams."""
    return (db.session.query(Team)
                      .all())


def get_team_by_name(db, team_name):
    """Return first Team object matching team_name."""
    return (db.session.query(Team)
                      .filter_by(name=team_name)
                      .first())


def get_players_from_team(db, team_name):
    """Return all players of team."""
    t = get_team_by_name(db, team_name)
    if t is not None:
        return (db.session.query(Player)
                          .filter_by(team=t)
                          .all())
    return None


def get_matches_by_day(db, day_num):
    """Return all matches scheduled for day day_num of the tournament."""
    match_date = START_DAY + datetime.timedelta(day_num - 1)
    return (db.session.query(Match)
                      .filter_by(date=match_date.date())
                      .all())
