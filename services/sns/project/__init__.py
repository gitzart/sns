import os
import warnings

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# ignore psycopg2 binary package `UserWarning`
warnings.filterwarnings('ignore', module='psycopg2')

db = SQLAlchemy()


def create_app(app_config=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.app import sns_blueprint
    app.register_blueprint(sns_blueprint)

    # shell context for flask cli
    app.shell_context_processor({'app': app, 'db': db})
    return app
