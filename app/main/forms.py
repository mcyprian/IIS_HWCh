from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField,
                     ValidationError, DateField, SelectField,
                     IntegerField, DateTimeField)
from wtforms.validators import (Required, Length, EqualTo,
                                NumberRange, InputRequired)

from app import db
from app.queries import get_employee


class TimeField(DateTimeField):
    """
    Same as DateTimeField, except stores a `time`.
    """

    def __init__(self, label=None, validators=None, format='%H:%M', **kwargs):
        super(TimeField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                self.data = datetime.strptime(
                    time_str, self.format).time()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid time value'))


class NotEqualTo(object):

    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(
                field.gettext("Invalid field name '{}'.".format(
                        self.fieldname)))
        if field.data == other.data and field.data != "EMPTY":
            raise ValidationError('Field cannot be equal to {}s.'.format(
                self.fieldname))


class UniqueList(object):

    def __init__(self, fieldslist):
        self.fieldslist = fieldslist

    def __call__(self, form, field):
        try:
            other_data = [form[item].data for item in self.fieldslist]
        except KeyError:
            raise ValidationError(
                field.gettext("Invalid field name in list"))
        if field.data in other_data:
            raise ValidationError('Field must be unique in the list.')


class NameForm(FlaskForm):
    name = StringField('Insert name', validators=[Required(), Length(0, 64)])
    submit = SubmitField('Search')


class UpdateEmployeeForm(FlaskForm):
    name = StringField('First name', [Length(0, 64)])
    surname = StringField('Last name', [Length(0, 64)])
    login = StringField('Login', [Length(0, 64)])
    date_of_birth = DateField("Date of birth:",
                              format='%d.%m.%Y',
                              description="Format: DD.MM.YYYY",
                              validators=[Required()])

    password = PasswordField('New Password', [
        EqualTo('confirm', message='Passwords must match'), Length(0, 128)])
    confirm = PasswordField('Repeat Password', [Length(0, 128)])
    submit = SubmitField('Submit')

    def validate_login(self, field):
        if field.data != self.emp.login and get_employee(db, self.login.data):
            raise ValidationError("Login already exist.")

    def __init__(self, *args, **kwargs):
        super(UpdateEmployeeForm, self).__init__(*args, **kwargs)
        self.emp = kwargs['emp']


class NewEmployeeForm(UpdateEmployeeForm):
    role = SelectField('* Role', choices=[('EMPLOYEE', 'employee'),
                                          ('MANAGER', 'manager'),
                                          ('ADMINISTRATOR', 'administrator')])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UpdateEmployeeForm, self).__init__(*args, **kwargs)
        for attr in ['name', 'surname', 'login', 'date_of_birth', 'password']:
            self[attr].validators.append(Required())
            self[attr].label.text = '* ' + self[attr].label.text

    def validate_login(self, field):
        pass


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


class UpdateTeamsForm(FlaskForm):
    home_team = SelectField('Home team', choices=[],
                            validators=[NotEqualTo('away_team')])
    away_team = SelectField('Away team', choices=[])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UpdateTeamsForm, self).__init__(*args, **kwargs)
        self.home_team.choices = kwargs['teams']
        self.away_team.choices = kwargs['teams']

    def validator(self):
        if self.home_team == self.away_team:
            raise ValidationError("Home and away team cannot be the same")


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


class UpdateMatchTime(FlaskForm):
    time = TimeField("* Time of the match:", description="Format: HH:MM")
    submit = SubmitField('Submit')


class RefereeUpdateForm(FlaskForm):
    head = SelectField('Head referee', choices=[], validators=[
        UniqueList(['first_line', 'second_line', 'video'])])
    first_line = SelectField('First line referee', choices=[], validators=[
        UniqueList(['head', 'second_line', 'video'])])
    second_line = SelectField('Second line referee', choices=[], validators=[
        UniqueList(['head', 'first_line', 'video'])])
    video = SelectField('Video referee', choices=[], validators=[
        UniqueList(['head', 'first_line', 'second_line'])])

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(RefereeUpdateForm, self).__init__(*args, **kwargs)
        for attr in ['head', 'first_line', 'second_line', 'video']:
            setattr(getattr(self, attr), 'choices', kwargs['referees'])


class UpdateGoalieForm(FlaskForm):
    goalie = SelectField('Goalie', choices=[])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UpdateGoalieForm, self).__init__(*args, **kwargs)
        self.goalie.choices = kwargs['goalies']


class UpdateFormationForm(FlaskForm):
    first_forward = SelectField('Forward 1', choices=[], validators=[
        UniqueList(['second_forward', 'third_forward'])])

    second_forward = SelectField('Forward 2', choices=[], validators=[
        UniqueList(['first_forward', 'third_forward'])])

    third_forward = SelectField('Forward 3', choices=[], validators=[UniqueList(
        ['first_forward', 'second_forward'])])

    first_defender = SelectField('Defender 1', choices=[], validators=[
        NotEqualTo('second_defender')])

    second_defender = SelectField('Defender 2', choices=[], validators=[
        NotEqualTo('first_defender')])

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UpdateFormationForm, self).__init__(*args, **kwargs)
        for attr in ['first', 'second', 'third']:
            setattr(getattr(self, attr + '_forward'),
                    'choices', kwargs['forwards'])

        self.first_defender.choices = kwargs['defenders']
        self.second_defender.choices = kwargs['defenders']
