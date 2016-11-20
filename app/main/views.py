from datetime import date, timedelta
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required

from app import db
from app.queries import (get_player_by_surname,
                         get_player_by_surname_regex,
                         get_player_by_id,
                         get_teams,
                         get_all_arenas,
                         get_matches_for_arena_by_day,
                         get_score,
                         get_most_productive,
                         get_num_of,
                         get_num_of_games,
                         get_all_players,
                         get_total_time,
                         get_all_employees,
                         get_team_by_name,
                         get_losses,
                         get_wins,
                         get_num_of_scored,
                         get_num_of_received,
                         get_members_of_team,
                         get_mvp)

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
    teams = {}
    for t in get_teams(db):
        coach = get_members_of_team(db, t, role='coach').pop()
        (mvp, points) = get_mvp(db, t)
        teams[t.name] = {
             "mvp": {
                 "id": mvp.id,
                 "points": points,
                 "full_name": "{} {}".format(mvp.name, mvp.surname)
             },
             "coach": {
                 "full_name": "{} {}".format(coach.name, coach.surname)
             }
        }
    return jsonify(teams)


@main.route("/players", methods=['GET', 'POST'])
@check_current_user
def players(user=None):
    form = NameForm()
    if form.validate_on_submit():
        search = form.name.data
        form.name.data = ''
        return redirect(url_for('.player_search', player_surname=search))
    top_players = {}
    for player, points in get_most_productive(db)[:9]:
        top_players[player] = (points,
                               get_num_of(db, player, 'goal'),
                               get_num_of(db, player, 'assist'))
    return render_template('players.html', form=form,
                           top_players=top_players,
                           user=user)


@main.route("/players/search/<player_surname>")
@check_current_user
def player_search(player_surname, user=None):
    if ' ' in player_surname:
        player_surname = player_surname.split()[-1]
    player = (get_player_by_surname(db, player_surname.title()) or
              get_player_by_surname_regex(db, player_surname.title()))
    if len(player) == 1:
        return redirect(url_for('.player_profile', player_id=player.pop().id))
    elif player == []:
        return render_template('player_profile.html',
                               player=None,
                               user=user)
    else:
        return render_template('player_search.html',
                               players=player,
                               name=player_surname,
                               user=user)


@main.route("/players/<player_id>")
@check_current_user
def player_profile(player_id, user=None):
    player = get_player_by_id(db, player_id)
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
    return render_template('standings.html', data="Various standings...",
                           user=user)


@main.route("/standings/data.json")
def standings_data():
    players = []
    for player in get_all_players(db):
        player_data = {
            'id': player.id,
            'name': player.name,
            'surname': player.surname,
            'team': player.team.code,
            'position': player.position,
            'points': (get_num_of(db, player, 'goal') +
                       get_num_of(db, player, 'assist')),
            'goals': get_num_of(db, player, 'goal'),
            'assists': get_num_of(db, player, 'assist'),
            'penalties': get_num_of(db, player, 'penalty'),
            'time': get_total_time(db, player) // 60
        }
        players.append(player_data)
    return jsonify(players)


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


@main.route("/settings")
def settings(user=None):
    return redirect(url_for(".employee_management"))


@main.route("/employee_management")
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def employee_management(user=None):
    return render_template('employee_management.html',
                           data="Content for admins.",
                           user=user)


@main.route("/employee_management/list.json")
def employee_list():
    employees = []
    for emp in get_all_employees(db):
        employee = {
            "name": emp.name,
            "surname": emp.surname,
            "login": emp.login,
            "role": emp.role
        }
        employees.append(employee)
    return jsonify(employees)


@main.route("/teams/<team_name>")
def team_profile(team_name):
    team = get_team_by_name(db, team_name)
    if team is not None:
        wins = get_wins(db, team, 0)
        wins_o = get_wins(db, team, 1)
        losses = get_losses(db, team, 0)
        losses_o = get_losses(db, team, 1)
        received = get_num_of_received(db, team)
        scored = get_num_of_scored(db, team)
        data = {
            "players": get_members_of_team(db, team, 'player'),
            "coachs": get_members_of_team(db, team, 'coach'),
            "assistants": get_members_of_team(db, team, 'assistant')
        }
        data["num_of_mem"] = len(
            data["players"]) + len(data["coachs"]) + len(data["assistants"])

        score = (wins*3) + (wins_o*2) + (losses_o)

        if ((scored + received) > 0):
            percents = 100/(scored+received)
            per_s = scored*percents
            per_r = received*percents
        else:
            per_s = 0
            per_r = 0

        return render_template('team_profile.html',
                               team=team,
                               scored=scored,
                               received=received,
                               data=data,
                               wins=wins,
                               losses=losses,
                               wins_o=wins_o,
                               losses_o=losses_o,
                               score=score,
                               per_s=per_s,
                               per_r=per_r)

    else:
        team = None
        return render_template('team_profile.html', team=team)


@main.route("/delete.json", methods=["POST"])
def delete(data):
    print(request.json)
