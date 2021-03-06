from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField

from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Case

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Innn')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    #username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=4096)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=4096)])
    submit = SubmitField('Submit')

class PostCase(FlaskForm):
    casename = TextAreaField('Set casename(*must input and unique)', validators=[DataRequired(), Length(min=1, max=16)])
    infect_id = TextAreaField('Set infect_id(Default is Null)', validators=[Length(min=0, max=128)])
    show_source = BooleanField('allow show infection source', default=False)
    show_result = BooleanField('allow show infection result', default=True)
    show_record = BooleanField('allow show exchange record', default=True)
    allow_post = BooleanField('allow submit', default=True)
    submit = SubmitField('PostCase')

class ManageCase(FlaskForm):
    infect_id = TextAreaField('Set infect_id(Default is Null)', validators=[Length(min=0, max=128)])
    show_source = BooleanField('allow show infection source')
    show_result = BooleanField('allow show infection result', default=True)
    show_record = BooleanField('allow show exchange', default=True)
    allow_post = BooleanField('allow submit', default=True)
    submit = SubmitField('Submit')

class InputGene(FlaskForm):
    inputgene = TextAreaField("", validators=[DataRequired(), Length(min=1, max=128)])
    submit = SubmitField('Input Gene')


class CreatSuper(FlaskForm):
    supername = TextAreaField("Input super user name", validators=[DataRequired(), Length(min=1, max=128)])
    submit = SubmitField('CreatSuperUser')