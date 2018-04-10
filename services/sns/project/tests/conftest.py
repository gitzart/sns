import pytest

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app(request):
    app = Flask(request.module.__name__)
    app.config.from_object('project.config.TestingConfig')
    return app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def db(app):
    return SQLAlchemy(app)
