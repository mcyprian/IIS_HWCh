from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Length, EqualTo


class NameForm(FlaskForm):
    name = StringField('Insert name', validators=[Required(), Length(0, 64)])
    submit = SubmitField('Search')


class UpdateEmployeeForm(FlaskForm):
    name = StringField('First name', [Length(0, 64)])
    surname = StringField('Last name', [Length(0, 64)])
    login = StringField('Login', [Length(0, 64)])
    password = PasswordField('New Password', [
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')
