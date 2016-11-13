from functools import wraps

from flask import abort
from flask_login import current_user

roles = {
    'EMPLOYEE': 0x0,
    'MANAGER': 0x1,
    'ADMINISTRATOR': 0xff
}


def requires_role(role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role < roles[role]:
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper


def check_current_user(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            user = current_user.login
        except AttributeError:
            user = None
        kwargs['user'] = user
        return f(*args, **kwargs)
    return wrapped