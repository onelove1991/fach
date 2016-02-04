from flask import render_template, flash, redirect, request, url_for
from flask.ext.login import (logout_user, login_required, login_user,
    current_user, current_app)

from . import auth
from .. import db
from ..models import User
from .forms import (LoginForm, RegistrationForm,ChangePasswordForm,
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm,
    )
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('main.index'))
    form  = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data,
            email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        token = new_user.generate_confirmation_token()
        send_email(new_user.email, 'Confirm Your Account',
            'auth/email/confirm', user=new_user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired!')
    return redirect(url_for('main.index'))

@auth.route('/confirm/')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash('Your are already confirmed!')
        return redirect(url_for('main.index'))
    else:
        token = current_user.generate_confirmation_token()
        print(
            current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'],
            current_app.config['SECRET_KEY'], current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'],
            current_app.config['FLASKY_ADMIN'], current_app.config['FLASKY_MAIL_SENDER'],
            current_app.config['MAIL_PORT'], current_app.config['MAIL_SERVER'],
            token, current_user.email)
        send_email(current_user.email, 'Confirm Your Account',
            'auth/email/confirm', user=current_user, token=token)
        flash('A new confirmation email has been send to your email.')
        return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Your have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('You have successfully changed your password!')
            redirect(url_for('auth.logout'))
            return redirect(url_for('auth.login'))
        flash('Please enter the correct password.')
    return render_template('auth/change_password.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                            'auth/email/reset_password', user=user,
                            token=token, next=request.args.get('next'))
            flash('An email with instructions to reset your password has '
                    'been sent to you.')
            return redirect(url_for('auth.login'))
        flash('Please enter a valid email.')
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.reset_password(token, form.password.data):
                flash('You have successfully reset password!')
                return redirect(url_for('auth.login'))
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address', 
                'auth/email/change_email', user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                        'address has been sent to you.')
            return redirect(url_for('main.index'))
        flash('Invalid email or password.')
    return render_template('auth/change_email.html', form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been changed.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
