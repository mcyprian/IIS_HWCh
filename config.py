import os
_basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'Replace this with a proper key.'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
