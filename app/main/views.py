from datetime import date, timedelta
from flask import render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user

from app import db
from app.storage import Team, Player
from app.queries import (get_player_by_surname,
                         get_player_by_surname_regex,
                         get_teams,
                         get_all_arenas,
                         get_matches_for_arena_by_day,
                         get_score)
from app.main import main
from app.main.forms import NameForm


@main.route('/')
def index():
    return render_template('index.html')


@main.route("/schedule/<day_num>")
def schedule(day_num):
    day_num = int(day_num)
    arenas = get_all_arenas(db)
    data = {}
    print (arenas)
    for arena in arenas:
        data[arena] = get_matches_for_arena_by_day(db, arena, day_num)
        print(data)
        for m in data[arena]:
            m.home_score = get_score(db, m, home=True)
            m.away_score = get_score(db, m, home=False)
            m.match_date = str(m.datetime.time())

    return render_template('schedule.html', data=data, day=day_num)


@main.route("/teams")
def teams():
    return render_template('teams.html', data="Overview of teams...")


@main.route("/teams/list.json")
def teams_list():
    return jsonify([t.name for t in get_teams(db)])


@main.route("/players", methods=['GET', 'POST'])
def players():
    form = NameForm()
    if form.validate_on_submit():
        search = form.name.data
        form.name.data = ''
        return redirect(url_for('.player_profile', player_surname=search))
    return render_template('players.html', form=form)


@main.route("/players/<player_surname>")
def player_profile(player_surname):
    player = (get_player_by_surname(db, player_surname)
              or get_player_by_surname_regex(db, player_surname))

    try:
        if isinstance(player, list):
            print(player)
            player = player.pop()
        player.age = (
            date.today() - player.date_of_birth) // timedelta(days=365.2425)
    except IndexError:
        player = None

    return render_template('player_profile.html', player=player)


@main.route("/standings")
def standings():
    return render_template('blank.html', data="Various standings...")


@main.route("/secret")
@login_required
def secret():
    print(current_user.is_authenticated)
    return render_template('blank.html', data="Secret content for logged in users...")
