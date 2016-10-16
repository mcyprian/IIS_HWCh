from flask import render_template, redirect, url_for
from datetime import date, timedelta

from app.storage import Team, Player
from app.home import home
from app.home.forms import NameForm


@home.route('/')
def index():
    return render_template('index.html')


@home.route("/schedule")
def schedule():
    return render_template('blank.html', data="Scheduled matches...")


@home.route("/teams")
def teams():
    return render_template('blank.html', data="Overview of teams...")


@home.route("/players", methods=['GET', 'POST'])
def players():
    form = NameForm()
    if form.validate_on_submit():
        search = form.name.data
        form.name.data = ''
        return redirect(url_for('.player_profile', player_name=search))
    return render_template('players.html', form=form)


@home.route("/players/<player_name>")
def player_profile(player_name):
    player = Player.query.filter_by(surname=player_name).first()
    if player is not None:
        player.age = (date.today() - player.date_of_birth) // timedelta(days=365.2425)
    return render_template('player_profile.html', player=player)


@home.route("/standings")
def standings():
    return render_template('blank.html', data="Various standings...")
