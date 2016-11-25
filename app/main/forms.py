from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField,
                     ValidationError, DateField, SelectField)
from wtforms.validators import Required, Length, EqualTo

from app import db
from app.queries import get_employee


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

    def validate_login(self, field):
        if field.data != self.login and get_employee(db, self.login.data):
            raise ValidationError("Login already exist.")


class NewEmployeeForm(UpdateEmployeeForm):
    date_of_birth = DateField("* Date of birth:",
                              format='%d.%m.%Y',
                              description="Format: DD.MM.YYYY",
                              validators=[Required()])

    role = SelectField('* Role', choices=[('EMPLOYEE', 'employee'),
                                          ('MANAGER', 'manager'),
                                          ('ADMINISTRATOR', 'administrator')])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(NewEmployeeForm, self).__init__(*args, **kwargs)
        for attr in ['name', 'surname', 'login', 'password']:
            self[attr].validators.append(Required())
            self[attr].label.text = '* ' + self[attr].label.text
