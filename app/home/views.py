from flask import render_template, redirect, url_for, jsonify
from datetime import date, timedelta

from app import db
from app.storage import Team, Player
from app.queries import (get_player_by_surname,
                         get_player_by_surname_regex,
                         get_teams)
from app.home import home
from app.home.forms import NameForm


@home.route('/')
def index():
    return render_template('index.html')


@home.route("/schedule")
def schedule():
    return render_template('schedule.html', data="Scheduled matches...")


@home.route("/teams")
def teams():
    return render_template('teams.html', data="Overview of teams...")


@home.route("/teams/list.json")
def teams_list():
    return jsonify([t.name for t in get_teams(db)])


@home.route("/players", methods=['GET', 'POST'])
def players():
    form = NameForm()
    if form.validate_on_submit():
        search = form.name.data
        form.name.data = ''
        return redirect(url_for('.player_profile', player_surname=search))
    return render_template('players.html', form=form)


@home.route("/players/<player_surname>")
def player_profile(player_surname):
    player = (get_player_by_surname(db, player_surname)
              or get_player_by_surname_regex(db, player_surname))

    try:
        if isinstance(player, list):
            print(player)
            player = player.pop()
        player.age = (date.today() - player.date_of_birth) // timedelta(days=365.2425)
    except IndexError:
        player = None

    return render_template('player_profile.html', player=player)


@home.route("/standings")
def standings():
    return render_template('blank.html', data="Various standings...")
