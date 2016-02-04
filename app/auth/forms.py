from flask.ext.wtf import Form
from wtforms import (StringField, PasswordField, BooleanField,
    SubmitField, ValidationError)
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64),
                                                            Email()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64),
        Email()])
    username = StringField('Username', validators=[
        Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                            'Username must have only letters, '
                                                            'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Password must match!')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(Form):
    old_password = PasswordField('Enter Your Current Password:',
        validators=[Required()])
    new_password = PasswordField('New Password:', 
        validators=[Required(), 
                        EqualTo('new_password2',
                                    message='Password must match!')])
    new_password2 = PasswordField('Confirm Password',
        validators=[Required()])
    submit = SubmitField('Change')

class PasswordResetRequestForm(Form):
    email = StringField('Email:', validators=[Required(), Length(1,64),
                                                                Email()])
    submit = SubmitField('Reset Password')

class PasswordResetForm(Form):
    email = StringField('Email:', validators=[Required(), Length(1,64),
                                                                Email()])
    password = PasswordField('New Password:', 
        validators=[Required(), 
                        EqualTo('password2', message='Password must match!')])
    password2 = PasswordField('Confirm Password',
        validators=[Required()])
    submit = SubmitField('Reset')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown email address.')

class ChangeEmailForm(Form):
    email = StringField('New Email:', validators=[Required(), Length(1,64),
                                                                Email()])
    password = PasswordField('Password:', validators=[Required()])
    submit = SubmitField('Reset')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The email you entered already exist!')
        if self.email == field.data:
            raise ValidationError('Please enter a new email.')

