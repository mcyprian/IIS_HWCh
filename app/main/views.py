from datetime import date, timedelta
from random import randrange
from flexmock import flexmock
from flask import (render_template, request, redirect, url_for,
                   jsonify, flash, abort)
from flask_login import login_required, current_user

from app import db
from app.settings import START_DAY
from app.queries import (get_player_by_surname,
                         get_player_by_surname_regex,
                         get_player_by_id,
                         get_teams,
                         get_all_arenas,
                         get_matches_for_arena_by_day,
                         get_matches_by_day,
                         get_score_or_none,
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
                         get_events_of_match,
                         get_event,
                         get_match_by_id,
                         get_mvp,
                         get_player_rand,
                         get_tm_by_id,
                         can_be_removed,
                         get_team_rand,
                         get_all_groups,
                         get_finished_match_rand,
                         get_all_referees,
                         get_ref_by_id,
                         get_formations_of_match,
                         get_formation_by_id,
                         get_player_of_team)

from app.storage import Player, TeamMember, Controls, Employee, Event, PlayedIn
from app.roles import requires_role, check_current_user, roles
from app.main import main
from app.main.forms import (NameForm, UpdateEmployeeForm, NewEmployeeForm,
                            UpdateEventForm, NewEventForm, UpdateTeamsForm,
                            NewPlayer, NewTeamMember, UpdateMatchTime,
                            RefereeUpdateForm, UpdateGoalieForm,
                            UpdateFormationForm)


@main.route('/')
@check_current_user
def index(user=None):
    team = get_team_rand(db) or flexmock(name="Missing data", code="EMP")
    player = get_player_rand(db) or flexmock(name="Missing",
                                             surname="data",
                                             team=team)
    difference = 3
    games1 = get_matches_by_day(db, difference + 1)
    if not games1:
        games1 = [flexmock(home_team=flexmock(name="Missing data", code='EMP'),
                           away_team=flexmock(name="Missing data", code='EMP'),
                           datetime=flexmock(time=lambda: "00:00"))]
    games2 = get_matches_by_day(db, difference + 2)
    if not games2:
        games2 = [flexmock(home_team=flexmock(name="Missing data", code='EMP'),
                           away_team=flexmock(name="Missing data", code='EMP'),
                           datetime=flexmock(time=lambda: "00:00"))]
    for game in games1:
        game.day = difference + 1
    for game in games2:
        game.day = difference + 2

    rand_match = get_finished_match_rand(db)

    return render_template('index.html', player=player,
                           team=team,
                           games=games1 + games2,
                           user=user,
                           rand_match=rand_match)


@main.route("/schedule")
def redirect_to_first_day():
    return redirect(url_for(".schedule", day_num=1))


@main.route("/schedule/<day_num>")
@check_current_user
def schedule(day_num, user=None):
    try:
        day_num = int(day_num)
        if day_num > 10:
            raise ValueError
    except ValueError:
        return abort(404)

    playoffs = [
        [('A1', 'B4'), ('A2', 'B3')],
        [('A3', 'B2'), ('A4', 'B1')],
        [('A1/B4', 'A4/B1'), ('A2/B3', 'A3/B2')],
        [('', ''), ('', '')]]
    arenas = get_all_arenas(db)
    data = {}
    for arena in arenas:
        data[arena] = get_matches_for_arena_by_day(db, arena, day_num)
        for m in data[arena]:
            m.home_score = get_score_or_none(db, m, home=True)
            m.away_score = get_score_or_none(db, m, home=False)
            m.match_date = str(m.datetime.time())
            if m.home_score is not None:
                m._home_score = m.home_score
                m._away_score = m.away_score
            if day_num >= 7:
                pair = playoffs[day_num - 7].pop()
            else:
                pair = ('Empty', 'Empty')
            m._home_team = m.home_team if m.home_team else flexmock(
                                                                    name=pair
                                                                    [0],
                                                                    code='EMP')
            m._away_team = m.away_team if m.away_team else flexmock(
                                                                    name=pair
                                                                    [1],
                                                                    code='EMP')

    return render_template('schedule.html', data=data, day=day_num, user=user)


@main.route("/schedule/formations/<match_id>")
@check_current_user
@requires_role('EMPLOYEE')
def match_formations(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)

    home_formations = get_formations_of_match(db, match_id, "home")
    away_formations = get_formations_of_match(db, match_id, "away")
    match = get_match_by_id(db, match_id)
    return render_template('formations.html',
                           home_formations=home_formations,
                           away_formations=away_formations,
                           match=match,
                           user=user)


@main.route('/schedule/formations/update/<role>/goalie/<fr_id>',
            methods=["GET", "POST"])
@check_current_user
@requires_role('MANAGER')
def update_goalie(role, fr_id, user=None):
    try:
        fr_id = int(fr_id)
    except ValueError:
        return abort(404)
    if role not in ["home", "away"]:
        abort(404)
    formation = get_formation_by_id(db, fr_id)
    if formation is None:
        return abort(404)

    if role == "home":
        team_goalies = get_player_of_team(
            db, formation.match.home_team, "goalie")
    else:
        team_goalies = get_player_of_team(
            db, formation.match.away_team, "goalie")

    goalies = []
    for g in team_goalies:
        goalies.append((str(g.id), '{} {}'.format(
            g.name, g.surname)))

    form = UpdateGoalieForm(goalies=goalies)
    if form.validate_on_submit():
        PlayedIn.query.filter_by(formation=formation).delete()

        g = PlayedIn(time=timedelta(minutes=60, seconds=0),
                     formation=formation, player=get_player_by_id(
                     db, form.goalie.data), role="goalie")
        db.session.add(g)
        db.session.commit()

        return redirect(url_for(".match_formations",
                                match_id=formation.match.id))

    title = "Set {} team goalie for the match {}".format(
        role, formation.match.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route('/schedule/formations/update/<role>/<fr_id>',
            methods=["GET", "POST"])
@check_current_user
@requires_role('MANAGER')
def update_formation(role, fr_id, user=None):

    try:
        fr_id = int(fr_id)
    except ValueError:
        return abort(404)
    if role not in ["home", "away"]:
        abort(404)
    formation = get_formation_by_id(db, fr_id)
    if formation is None:
        return abort(404)

    if role == "home":
        team_forwards = get_player_of_team(
            db, formation.match.home_team, "forward")
        team_defenders = get_player_of_team(
            db, formation.match.home_team, "defender")
    else:
        team_forwards = get_player_of_team(
            db, formation.match.away_team, "forward")
        team_defenders = get_player_of_team(
            db, formation.match.away_team, "defender")

    forwards = []
    for f in team_forwards:
        forwards.append((str(f.id), '{} {}'.format(
            f.name, f.surname)))

    defenders = []
    for d in team_defenders:
        defenders.append((str(d.id), '{} {}'.format(
            d.name, d.surname)))

    form = UpdateFormationForm(forwards=forwards, defenders=defenders)
    if form.validate_on_submit():
        PlayedIn.query.filter_by(formation=formation).delete()

        f1 = PlayedIn(time=timedelta(minutes=randrange(5, 20),
                                     seconds=randrange(60)),
                      formation=formation, player=get_player_by_id(
                     db, form.first_forward.data), role="forward")

        f2 = PlayedIn(time=timedelta(minutes=randrange(5, 20),
                                     seconds=randrange(60)),
                      formation=formation, player=get_player_by_id(
                     db, form.second_forward.data), role="forward")

        f3 = PlayedIn(time=timedelta(minutes=randrange(5, 20),
                                     seconds=randrange(60)),
                      formation=formation, player=get_player_by_id(
                     db, form.third_forward.data), role="forward")

        d1 = PlayedIn(time=timedelta(minutes=randrange(5, 20),
                                     seconds=randrange(60)),
                      formation=formation, player=get_player_by_id(
                     db, form.first_defender.data), role="defender")

        d2 = PlayedIn(time=timedelta(minutes=randrange(5, 20),
                                     seconds=randrange(60)),
                      formation=formation, player=get_player_by_id(
                     db, form.second_defender.data), role="defender")

        player_list = [f1, f2, f3, d1, d2]
        formation.palyedins = player_list

        db.session.add_all(player_list)
        db.session.commit()

        return redirect(url_for(".match_formations",
                                match_id=formation.match.id))

    title = "Set {} team formation for the match {}".format(
        role, formation.match.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route("/schedule/events/<match_id>")
@check_current_user
@requires_role('EMPLOYEE')
def match_events(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)
    events = get_events_of_match(db, match_id)
    match = get_match_by_id(db, match_id)
    return render_template('events.html', events=events,
                           match=match, user=user)


@main.route("/schedule/events/update/<event_id>", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def update_event(event_id, user=None):
    try:
        event_id = int(event_id)
    except ValueError:
        return abort(404)

    ev = get_event(db, event_id=event_id)
    if not ev:
        return abort(404)
    teams = [("home", ev.match.home_team.name),
             ("away", ev.match.away_team.name)]
    match_participants = (
        get_members_of_team(db, ev.match.home_team, role='player') +
        get_members_of_team(db, ev.match.away_team, role='player'))
    players = [((str(ev.player.id), '{} {} ({})'.format(
        ev.player.name, ev.player.surname, ev.player.team.code)))]
    for player in match_participants:
        if player == ev.player:
            continue
        players.append((str(player.id), '{} {} ({})'.format(
            player.name, player.surname, player.team.code)))
    form = UpdateEventForm(teams=teams, players=players)
    title = "Update of event number {}".format(ev.id)

    if form.validate_on_submit():
        if form.code.data:
            ev.code = form.code.data
        ev.time = timedelta(minutes=form.minutes.data,
                            seconds=form.seconds.data)
        if form.team.data == "home":
            ev.team = ev.match.home_team
        else:
            ev.team = ev.match.away_team
        ev.player = get_player_by_id(db, int(form.player.data))
        ev.employee = current_user
        db.session.commit()

        return redirect(url_for('.match_events', match_id=ev.match.id))
    return render_template('quick_form.html',
                           page_title=title,
                           form=form,
                           user=user)


@main.route("/schedule/events/new/<match_id>", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('EMPLOYEE')
def new_event(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)

    m = get_match_by_id(db, match_id)
    if not m:
        return abort(404)

    teams = [("home", m.home_team.name),
             ("away", m.away_team.name)]

    match_participants = (
        get_members_of_team(db, m.home_team, role='player') +
        get_members_of_team(db, m.away_team, role='player'))

    players = []
    for player in match_participants:
        players.append((str(player.id), '{} {} ({})'.format(
            player.name, player.surname, player.team.code)))

    form = NewEventForm(teams=teams, players=players)

    if form.validate_on_submit():
        code = form.code.data
        time = timedelta(minutes=form.minutes.data,
                         seconds=form.seconds.data)
        if form.team.data == "home":
            team = m.home_team
        else:
            team = m.away_team
        player = get_player_by_id(db, int(form.player.data))
        employee = current_user
        ev = Event(code=code, time=time, employee=employee, player=player,
                   match=m, team=team)
        db.session.add(ev)
        db.session.commit()
        return redirect(url_for('.match_events', match_id=m.id))
    title = "New event in match {}".format(m.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route("/schedule/events/delete.json", methods=["POST"])
def delete_event():
    data = request.get_json()
    ev = get_event(db, event_id=data["id"])
    if not ev:
        response_data = {"status": "failure", "id": data["id"]}
    else:
        db.session.delete(ev)
        db.session.commit()
        response_data = {"status": "success", "id": data["id"]}
    return jsonify(response_data)


@main.route("/schedule/teams/<match_id>", methods=['GET', 'POST'])
@check_current_user
@requires_role('MANAGER')
def update_teams(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)
    match = get_match_by_id(db, match_id)
    if match is None:
        return abort(404)

    teams = []
    for team in get_teams(db):
        teams.append((team.name, '{} ({})'.format(
            team.name, team.group.code)))

    teams.append(('EMPTY', 'EMPTY'))
    form = UpdateTeamsForm(teams=teams)
    if form.validate_on_submit():
        match.home_team = get_team_by_name(db, form.home_team.data)
        match.away_team = get_team_by_name(db, form.away_team.data)
        db.session.commit()
        day_num = (match.datetime - START_DAY).days + 1
        return redirect(url_for(".schedule", day_num=day_num))

    title = "Set teams of match {}".format(match.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route('/schedule/time/<match_id>', methods=["GET", "POST"])
@check_current_user
@requires_role('MANAGER')
def update_match_time(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)
    match = get_match_by_id(db, match_id)
    if match is None:
        return abort(404)

    form = UpdateMatchTime()
    if form.validate_on_submit():
        match.datetime = match.datetime.replace(hour=form.time.data.hour,
                                                minute=form.time.data.minute)
        db.session.commit()
        day_num = (match.datetime - START_DAY).days + 1
        return redirect(url_for(".schedule", day_num=day_num))

    title = "Set time of the match {}".format(match.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route('/schedule/referees/<match_id>', methods=["GET", "POST"])
@check_current_user
@requires_role('MANAGER')
def set_referees(match_id, user=None):
    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)
    match = get_match_by_id(db, match_id)
    if match is None:
        return abort(404)

    referees = []
    for ref in get_all_referees(db):
        referees.append((str(ref.id), '{} {}'.format(
            ref.name, ref.surname)))

    form = RefereeUpdateForm(referees=referees)
    if form.validate_on_submit():
        Controls.query.filter_by(match=match).delete()

        c1 = Controls(match=match, referee=get_ref_by_id(
            db, int(form.head.data)), role='head')

        c2 = Controls(match=match, referee=get_ref_by_id(
            db, int(form.first_line.data)), role='line')

        c3 = Controls(match=match, referee=get_ref_by_id(
            db, int(form.second_line.data)), role='line')

        c4 = Controls(match=match, referee=get_ref_by_id(
            db, int(form.video.data)), role='video')

        control_list = [c1, c2, c3, c4]
        match.controls = control_list

        db.session.add_all(control_list)
        db.session.commit()
        day_num = (match.datetime - START_DAY).days + 1
        return redirect(url_for(".schedule", day_num=day_num))

    title = "Set referees of the match {}".format(match.id)
    return render_template('quick_form.html',
                           form=form,
                           page_title=title,
                           user=user)


@main.route("/teams")
@check_current_user
def teams(user=None):
    return render_template('teams.html', user=user)


@main.route("/teams/list.json")
def teams_list():
    teams = {}
    for t in get_teams(db):
        try:
            coach = get_members_of_team(db, t, role='coach').pop()
        except IndexError:
            coach = flexmock(name='Missing', surname='Coach')
        (mvp, points) = get_mvp(db, t)
        if not mvp:
            (mvp, points) = (flexmock(name="Missing", surname="Player"), 0)
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
    for player in team_members["players"]:
        player.del_flag = can_be_removed(db, player)

    if team is not None:
        return render_template('teams_management.html', team=team,
                               team_members=team_members, user=user)
    else:
        return abort(404)


@main.route("/team_management/<team_name>/new_player", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('MANAGER')
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
            return render_template("new_player.html", form=form, user=user)
    else:
        return abort(404)


@main.route("/team_management/<team_name>/new_member", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('MANAGER')
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
            return render_template("new_member.html", form=form, user=user)
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
            name=member.name,
            surname=member.surname,
            date_of_birth=member.date_of_birth,
            role=member.role)
    else:
        form = NewPlayer(
            name=member.name,
            surname=member.surname,
            date_of_birth=member.date_of_birth,
            number=int(member.number),
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
            return render_template("edit_member.html", form=form, user=user)
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


@main.route("/settings")
def settings(user=None):
    return redirect(url_for(".employees"))


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
    emp = get_employee(db, login=login)
    if not emp:
        return abort(404)
    form = UpdateEmployeeForm(name=emp.name,
                              surname=emp.surname,
                              login=emp.login,
                              date_of_birth=emp.date_of_birth,
                              emp=emp)
    if not emp:
        return abort(404)
    if form.validate_on_submit():
        for attr in ("name", "surname", "login", "password", "date_of_birth"):
            value = getattr(form, attr, None)
            if value and value.data:
                setattr(emp, attr, value.data)
        db.session.commit()
        flash("Employee data successfuly updated.")
        return redirect(url_for(".employees"))
    title = "Update of employee {}".format(emp.login)
    return render_template("quick_form.html",
                           user=user,
                           page_title=title,
                           form=form)


@main.route("/employees/new", methods=['GET', 'POST'])
@login_required
@check_current_user
@requires_role('ADMINISTRATOR')
def new_employee(user=None):
    form = NewEmployeeForm()
    if form.validate_on_submit():
        emp = Employee(name=form.name.data,
                       surname=form.surname.data,
                       login=form.login.data,
                       date_of_birth=form.date_of_birth.data,
                       role=roles[form.role.data],
                       password=form.password.data)

        db.session.add(emp)
        db.session.commit()
        return redirect(url_for(".employees"))
    return render_template("quick_form.html",
                           user=user,
                           page_title="New employee",
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


@main.route("/employees/manage.json", methods=["POST"])
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


def get_team_points(team, poi=True):
    wins = get_wins(db, team, 0)
    wins_o = get_wins(db, team, 1)
    losses_o = get_losses(db, team, 1)

    if poi is True:
        score = (wins * 3) + (wins_o * 2) + (losses_o)
        return score
    else:
        losses = get_losses(db, team, 0)
        data = {
            "wins": wins,
            "wins_o": wins_o,
            "losses": losses,
            "losses_o": losses_o
        }
        return data


@main.route("/teams/<team_name>")
@check_current_user
def team_profile(team_name, user=None):
    team = get_team_by_name(db, team_name)
    if team is not None:
        status = get_team_points(team, False)
        received = get_num_of_received(db, team)
        scored = get_num_of_scored(db, team)
        data = {
            "players": get_members_of_team(db, team, 'player'),
            "coachs": get_members_of_team(db, team, 'coach'),
            "assistants": get_members_of_team(db, team, 'assistant')
        }
        for key, value in data.items():
            if not value:
                data[key] = [flexmock(name="Missing", surname="Member")]
        data["num_of_mem"] = len(
            data["players"]) + len(data["coachs"]) + len(data["assistants"])

        score = get_team_points(team, True)

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
                               status=status,
                               score=score,
                               per_s=per_s,
                               per_r=per_r,
                               user=user)

    else:
        return abort(404)


@main.route('/match_profile/<match_id>')
@check_current_user
def match_profile(match_id, user=None):

    try:
        match_id = int(match_id)
    except ValueError:
        return abort(404)

    match = get_match_by_id(db, match_id)
    if match is not None:
        home_score = get_score_or_none(db, match, home=True)
        away_score = get_score_or_none(db, match, home=False)
        events = get_events_of_match(db, match_id)

        return render_template('match_profile.html', match=match,
                               events=events,
                               home_score=home_score,
                               away_score=away_score)

    else:
        return abort(404)


@main.route('/groups')
@check_current_user
def groups(user=None):

    datas = []
    groups = get_all_groups(db)
    for t in groups:
        datas.append([(g.name, get_team_points(g, True)) for g in t.teams])

    for i in datas:
        i.sort(key=lambda tup: tup[1], reverse=True)

    return render_template('groups.html', groups=groups,
                           datas=datas, user=user)
