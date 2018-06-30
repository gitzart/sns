import pytest

from project import create_app, db as database
from project.api.models.enums import Gender
from project.api.models.user import User


@pytest.fixture(scope='session')
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
    with app.app_context():
        database.create_all()
        yield database
        database.session.remove()
        database.drop_all()


@pytest.fixture
def setup(db):
    users = [
        dict(
            first_name='rory',
            last_name='williams',
            gender=Gender.MALE,
            email='rory@email.com',
            password='roryspassword'
        ),
        dict(
            first_name='amy',
            last_name='pond',
            gender=Gender.FEMALE,
            email='amy@email.com',
            password='amyspassword'
        ),
        dict(
            first_name='doctor',
            last_name='who',
            gender=Gender.OTHERS,
            email='doctor@email.com',
            password='doctorspassword'
        ),
        dict(
            first_name='bill',
            last_name='potts',
            gender=Gender.FEMALE,
            email='bill@email.com',
            password='billspassword'
        ),
        dict(
            first_name='song',
            last_name='river',
            gender=Gender.FEMALE,
            email='song@email.com',
            password='songspassword'
        ),
    ]
    db.session.bulk_insert_mappings(User, users)
    db.session.commit()
