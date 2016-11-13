from datetime import date, timedelta
from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required

from app import db
from app.queries import (get_player_by_surname,
                         get_player_by_surname_regex,
                         get_teams,
                         get_all_arenas,
                         get_matches_for_arena_by_day,
                         get_score,
                         get_most_productive,
                         get_num_of,
                         get_num_of_games)
from app.roles import requires_role, check_current_user
from app.main import main
from app.main.forms import NameForm


@main.route('/')
@check_current_user
def index(user=None):
    return render_template('index.html', user=user)


@main.route("/schedule/<day_num>")
@check_current_user
def schedule(day_num, user=None):
    day_num = int(day_num)
    arenas = get_all_arenas(db)
    data = {}
    for arena in arenas:
        data[arena] = get_matches_for_arena_by_day(db, arena, day_num)
        for m in data[arena]:
            m.home_score = get_score(db, m, home=True)
            m.away_score = get_score(db, m, home=False)
            m.match_date = str(m.datetime.time())

    return render_template('schedule.html', data=data, day=day_num, user=user)


@main.route("/teams")
@check_current_user
def teams(user=None):
    return render_template('teams.html', data="Overview of teams...", user=user)


@main.route("/teams/list.json")
def teams_list():
    return jsonify([t.name for t in get_teams(db)])


@main.route("/players", methods=['GET', 'POST'])
@check_current_user
def players(user=None):
    form = NameForm()
    if form.validate_on_submit():
        search = form.name.data
        form.name.data = ''
        return redirect(url_for('.player_profile', player_surname=search))
    top_players = {}
    for player, points in get_most_productive(db)[:9]:
        top_players[player] = (points,
                               get_num_of(db, player, 'goal'),
                               get_num_of(db, player, 'assist'))
    return render_template('players.html', form=form,
                           top_players=top_players,
                           user=user)


@main.route("/players/<player_surname>")
@check_current_user
def player_profile(player_surname, user=None):
    player = (get_player_by_surname(db, player_surname)
              or get_player_by_surname_regex(db, player_surname))
    if isinstance(player, list):
        if player !=  []:
            return render_template('player_search.html',
                                   players=player,
                                   name=player_surname,
                                   user=user)
        else:
            player = None
    else:
        try:
            player.age = (
                date.today() - player.date_of_birth) // timedelta(days=365.2425)
            player.games = get_num_of_games(db, player)
            player.goals = get_num_of(db, player, 'goal')
            player.assists = get_num_of(db, player, 'assist')
            player.penalties = get_num_of(db, player, 'penalty')
            player.points = player.goals + player.assists
        except AttributeError:
            player = None
    return render_template('player_profile.html', player=player, user=user)


@main.route("/standings")
@check_current_user
def standings(user=None):
    return render_template('blank.html', data="Various standings...", user=user)


@main.route("/secret")
@check_current_user
@login_required
def secret(user=None):
    return render_template('blank.html',
                           data="Secret content for logged in users...",
                           user=user)


@main.route("/championship_management")
@login_required
@check_current_user
@requires_role('MANAGER')
def championship_management(user=None):
    return render_template('blank.html',
                           data="Only managers can see this.",
                           user=user)


@main.route("/employee_management")
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def employee_management(user=None):
    return render_template('blank.html', data="Content for admins.", user=user)
