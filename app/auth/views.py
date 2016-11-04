from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.auth import auth
from app.storage.employee import Employee
from app.auth.forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(login=form.login.data).first()
        print(user)
        if user is not None and user.verify_password(form.password.data):
            print("User: {} logged in".format(user))
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
