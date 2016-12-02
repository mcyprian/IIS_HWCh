#!/usr/bin/env python3
import os
from datetime import timedelta

from flask import session
from flask_script import Manager, Shell

from app import create_app, db
from app.queries import *
from app.storage import *
from db_init import fill_db, recreate_all

app = create_app(os.environ.get('IIS_CONFIG', 'default'))
manager = Manager(app)


@app.before_request
def session_expiration():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=2)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        Team=Team,
        TeamMember=TeamMember,
        Event=Event,
        Employee=Employee,
        Player=Player,
        Group=Group,
        Match=Match,
        Referee=Referee,
        Controls=Controls,
        Formation=Formation,
        PlayedIn=PlayedIn,
        fill_db=fill_db)

manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def recreate_db():
    print("Dropping and recreating all tables...")
    recreate_all()
    print("Inserting data to recreated tables...")
    fill_db()
    db.session.commit()
    print("Done.")


@manager.command
def init_db():
    db.create_all()
    print("DB tables created.")
    fill_db()
    print("Example data inserted.")
    db.session.commit()
    print("Done.")

if __name__ == '__main__':
    manager.run()
