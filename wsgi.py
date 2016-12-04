#!/usr/bin/env python3
import os
from datetime import timedelta

from flask import session

from app import create_app

application = create_app(os.environ.get('IIS_CONFIG', 'default'))


@application.before_request
def session_expiration():
    session.permanent = True
    application.permanent_session_lifetime = timedelta(minutes=2)
