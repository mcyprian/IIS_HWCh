import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from flask_moment import Moment

from config import config_dict

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()


def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_mode])

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    return app
