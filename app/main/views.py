from datetime import date, timedelta
from flask import (render_template, request, redirect, url_for,
                   jsonify, flash, abort)
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
                         get_employee,
                         get_all_employees,
                         get_team_by_name,
                         get_losses,
                         get_wins,
                         get_num_of_scored,
                         get_num_of_received,
                         get_members_of_team,
                         get_tm_by_id,
                         get_mvp)

from app.roles import requires_role, check_current_user, roles
from app.main import main
from app.main.forms import (NameForm, UpdateEmployeeForm,
                            NewPlayer, NewTeamMember)

from app.storage import Player, TeamMember


@main.route('/')
@check_current_user
def index(user=None):
    return render_template('index.html', user=user)


@main.route("/schedule")
def redirect_to_first_day():
    return redirect(url_for(".schedule", day_num=1))


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
    return render_template('teams.html', user=user)


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


@main.route("/team_management/<team_name>", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('EMPLOYEE')
def team_management(team_name, user=None):
    data = request.get_json()
    if data is not None:
        player = get_tm_by_id(db, data["rm"])
        db.session.delete(player)
        db.session.commit()
    team = get_team_by_name(db, team_name)
    team_members = {"players": get_members_of_team(db, team, role='player'),
                    "coach": get_members_of_team(db, team, role='coach'),
                    "assistants": get_members_of_team(
                        db, team, role='assistant')}
    if team is not None:
        return render_template('teams_management.html', team=team,
                               team_members=team_members, user=user)
    else:
        return abort(404)


@main.route("/team_management/<team_name>/new_player", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('EMPLOYEE')
def new_player(team_name, user=None):
    form = NewPlayer()
    team = get_team_by_name(db, team_name)
    if team is not None:
        if form.validate_on_submit():
            player = Player(name=form.name.data,
                            surname=form.surname.data,
                            date_of_birth=form.date_of_birth.data,
                            role="player",
                            team=team,
                            number=form.number.data,
                            position=form.position.data,
                            club=form.club.data)
            db.session.add(player)
            db.session.commit()
            return redirect(url_for(".team_management", team_name=team_name,
                                    user=user))
        else:
            return render_template("new_player.html", form=form)
    else:
        return abort(404)


@main.route("/team_management/<team_name>/new_member", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('EMPLOYEE')
def new_member(team_name, user=None):
    form = NewTeamMember()
    team = get_team_by_name(db, team_name)
    if team is not None:
        if form.validate_on_submit():
            member = TeamMember(name=form.name.data,
                                surname=form.surname.data,
                                date_of_birth=form.date_of_birth.data,
                                role=form.role.data,
                                team=team)
            db.session.add(member)
            db.session.commit()
            return redirect(url_for(".team_management", team_name=team_name,
                                    user=user))
        else:
            return render_template("new_member.html", form=form)
    else:
        return abort(404)


@main.route("/team_management/<team_name>/edit/<member_id>",
            methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('EMPLOYEE')
def edit_member(team_name, member_id, user=None):
    team = get_team_by_name(db, team_name)
    member = get_tm_by_id(db, member_id)
    if member.role != "player":
        form = NewTeamMember(
            edit=True,
            name=member.name,
            surname=member.surname,
            birth=member.date_of_birth,
            role=member.role)
    else:
        form = NewPlayer(
            edit=True,
            name=member.name,
            surname=member.surname,
            birth=member.date_of_birth,
            jersey=int(member.number),
            position=member.position,
            club=member.club)
    if team is not None and member is not None:
        if form.validate_on_submit():
            member.name = form.name.data
            member.surname = form.surname.data
            member.date_of_birth = form.date_of_birth.data
            if member.role != "player":
                member.role = form.role.data
            else:
                member.number = form.number.data
                member.position = form.position.data
                member.club = form.club.data
            db.session.commit()
            return redirect(url_for(".team_management", team_name=team_name,
                                    user=user))
        else:
            return render_template("edit_member.html", form=form)
    else:
        return abort(404)


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


@main.route("/employees")
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def employees(user=None):
    employees = get_all_employees(db)
    return render_template('employees.html',
                           user=user,
                           employees=employees)


@main.route("/employees/update/<login>", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def update_employee(login, user=None):
    form = UpdateEmployeeForm()
    emp = get_employee(db, login=login)
    if not emp:
        return abort(404)
    if form.validate_on_submit():
        for attr in ("name", "surname", "login", "password"):
            value = getattr(form, attr, None)
            if value and value.data:
                setattr(emp, attr, value.data)
        db.session.commit()
        flash("Employee data successfuly updated.")
        return redirect(url_for(".employees"))
    return render_template("employee_update.html",
                           user=user,
                           form=form)


@main.route("/employees/list.json")
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


@main.route("/employees/manage.json", methods=["GET", "POST"])
def manage_employees():
    data = request.get_json()
    emp = get_employee(db, login=data["login"])
    if emp is not None:
        if data["action"] == "promote":
            if emp.role < roles['ADMINISTRATOR']:
                emp.role += 1
        elif data["action"] == "demote":
            if emp.role > roles["EMPLOYEE"]:
                emp.role -= 1
        elif data["action"] == "remove":
            db.session.delete(emp)

        db.session.commit()
        response_data = {
            "action": data["action"],
            "status": "success",
            "id": emp.id,
            "name": emp.name,
            "surname": emp.surname,
            "login": emp.login,
            "role": emp.role
        }
    else:
        response_data = {
            "action": data["action"],
            "status": "failure"
        }
    return jsonify(response_data)


@main.route("/teams/<team_name>")
@check_current_user
def team_profile(team_name, user=None):
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

        score = (wins * 3) + (wins_o * 2) + (losses_o)

        if ((scored + received) > 0):
            percents = 100 / (scored + received)
            per_s = scored * percents
            per_r = received * percents
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
                               per_r=per_r,
                               user=user)

    else:
        team = None
        return render_template('team_profile.html', team=team)
