#!/usr/bin/env python3

from flask_script import Manager, Shell

from app import create_app, db
from app.storage import *
from db_init import fill_db

app = create_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Team=Team, TeamMember=TeamMember,
                Event=Event, Employee=Employee, Player=Player, Group=Group,
                Match=Match, Referee=Referee, Controls=Controls, Formation=Formation,
                PlayedIn=PlayedIn, fill_db=fill_db)

manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
