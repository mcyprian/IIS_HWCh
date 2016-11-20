from flask import render_template

from app.main import main
from app.roles import check_current_user


@main.app_errorhandler(404)
@check_current_user
def page_not_found(e, user=None):
    print(user)
    return render_template('404.html', user=user), 404


@main.app_errorhandler(500)
@check_current_user
def internal_error(e, user=None):
    return render_template('500.html', user=user), 500


@main.app_errorhandler(403)
@check_current_user
def forbidden(e, user=None):
    return render_template('403.html', user=user), 403
