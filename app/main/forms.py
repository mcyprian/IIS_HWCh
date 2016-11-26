from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField,
                     ValidationError, DateField, SelectField,
                     IntegerField)
from wtforms.validators import (Required, Length, EqualTo,
                                NumberRange, InputRequired)

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


class UpdateEventForm(FlaskForm):
    code = SelectField('Type', choices=[('shot', 'shot'),
                                        ('offside', 'offside'),
                                        ('interference', 'interference'),
                                        ('goal', 'goal'),
                                        ('penalty', 'penalty')])
    minutes = IntegerField('* Minute', validators=[NumberRange(min=0, max=60),
                                                   InputRequired()])
    seconds = IntegerField('* Second', validators=[NumberRange(min=0, max=60),
                                                   InputRequired()])
    team = SelectField('Team', choices=[])
    player = SelectField('Player', choices=[])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UpdateEventForm, self).__init__(*args, **kwargs)
        self.team.choices = kwargs['teams']
        self.player.choices = kwargs['players']


class NewEventForm(UpdateEventForm):

    def __init__(self, *args, **kwargs):
        super(NewEventForm, self).__init__(*args, **kwargs)
        self.code.validators.append(Required())
        self.code.label.text = '* ' + self.code.label.text
