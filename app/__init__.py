from flask import (Flask, render_template, request, session,
    url_for, redirect, flash)
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
from flask.ext.script import Shell, Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.wtf import Form
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown

from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.debug = True
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    db = SQLAlchemy(app)
    bootstrap = Bootstrap(app)
    moment = Moment(app)
    manager = Manager(app)
    mail = Mail(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    return app