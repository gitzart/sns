import os
import warnings

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate


# ignore psycopg2 binary package `UserWarning`
warnings.filterwarnings('ignore', module='psycopg2')

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
toolbar = DebugToolbarExtension()


def create_app(app_config=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    toolbar.init_app(app)

    # register blueprints
    from project.api.app import sns_blueprint
    app.register_blueprint(sns_blueprint)

    # shell context for flask cli
    app.shell_context_processor({'app': app, 'db': db})
    return app
