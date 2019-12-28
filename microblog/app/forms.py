from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Usernameee', validators=[DataRequired()])
    password = PasswordField('Passwordddddd', validators=[DataRequired()])
    remember_me = BooleanField('Remember Meee')
    submit = SubmitField('Sign Innn')