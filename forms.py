"""Forms for authentication and user management"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from models import User

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    api_base_url = StringField('API Base URL (Optional)', validators=[Optional(), Length(max=255)])
    api_key = StringField('API Key (Optional)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class ProfileForm(FlaskForm):
    """User profile update form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    api_base_url = StringField('API Base URL', validators=[Optional(), Length(max=255)])
    api_key = StringField('API Key', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class SaveQueryForm(FlaskForm):
    """Save API query form"""
    name = StringField('Query Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description (Optional)', validators=[Optional(), Length(max=500)])
    is_favorite = BooleanField('Mark as Favorite')
    submit = SubmitField('Save Query')
