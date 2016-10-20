import os
from datetime import timedelta
_basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'Replace this with a proper key.'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://127.9.205.2:5432'

config_dict = {
    'devel': DevelConfig,
    'production': ProductionConfig,
    'default': DevelConfig
}
