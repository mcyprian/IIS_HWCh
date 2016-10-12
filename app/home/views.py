from flask import render_template

from app.models import TeamMember
from app.home import home
from app.home.forms import NameForm


@home.route('/')
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
    return render_template('index.html', form=form, name=name)


@home.route("/schedule")
def schedule():
    return render_template('blank.html', data="Scheduled matches...")


@home.route("/teams")
def teams():
    return render_template('blank.html', data="Overview of teams...")


@home.route("/players")
def players():
    search = 'Ovechkin'
    player = TeamMember.query.filter_by(surname=search).first()
    return render_template('player.html', player=player)


@home.route("/standings")
def standings():
    return render_template('blank.html', data="Various standings...")
