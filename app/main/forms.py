from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField,
                     ValidationError, DateField, SelectField,
                     IntegerField)
from wtforms.validators import Required, Length, EqualTo, NumberRange

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


class NewPlayer(FlaskForm):
    name = StringField('* First name:', validators=[Required(), Length(0, 64)])
    surname = StringField('* Last name:',
                          validators=[Required(), Length(0, 64)])
    date_of_birth = DateField("* Date of birth:", format='%d.%m.%Y',
                              description="Format: DD.MM.YYYY",
                              validators=[Required()])
    number = IntegerField('* Number for jersey:',
                          validators=[
                              Required(),
                              NumberRange(
                                  min=1,
                                  max=99,
                                  message="Choose number in range 1-99")])
    position = SelectField('* Position', choices=[
        ('goalie', 'Goalie'),
        ('defender', 'Defender'),
        ('forward', 'Forward')])
    club = StringField('Club:', validators=[Length(0, 64)])
    submit = SubmitField('Add')

    def __init__(self, edit=False, *args, **kwargs):
        super(NewPlayer, self).__init__(*args, **kwargs)
        if edit:
            self.name.default = kwargs['name']
            self.surname.default = kwargs['surname']
            self.date_of_birth.default = kwargs['birth']
            self.number.default = kwargs['jersey']
            self.position.default = kwargs['position']
            self.club.default = kwargs['club']


class NewTeamMember(FlaskForm):
    name = StringField('* First name:', validators=[Required(), Length(0, 64)])
    surname = StringField('* Last name:',
                          validators=[Required(), Length(0, 64)])
    date_of_birth = DateField("* Date of birth:", format='%d.%m.%Y',
                              description="Format: DD.MM.YYYY",
                              validators=[Required()])
    role = SelectField('* Role', choices=[
        ('coach', 'Coach'),
        ('assistant', 'Assistant')])
    submit = SubmitField('Add')

    def __init__(self, edit=False, *args, **kwargs):
        super(NewTeamMember, self).__init__(*args, **kwargs)
        if edit:
            self.name.default = kwargs['name']
            self.surname.default = kwargs['surname']
            self.date_of_birth.default = kwargs['birth']
            self.role.default = kwargs['role']
