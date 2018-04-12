import pytest

from project import create_app, db as database


@pytest.fixture(scope='module')
def app(request):
    app = create_app()
    app.config.from_object('project.config.TestingConfig')
    return app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def db(app):
    database.create_all()
    yield database
    database.session.remove()
    database.drop_all()
