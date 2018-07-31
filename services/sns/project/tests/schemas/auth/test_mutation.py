import pytest

from flask import current_app
from graphene import test

from project import bcrypt
from project.api.models.enums import Gender
from project.api.models.auth import BlacklistToken, get_new_token, verify_token
from project.api.models.user import User
from project.api.schemas import schema


client = test.Client(schema)
password = 'my precious'

login_mutation = '''
    mutation LoginUser($email: String!, $password: String!) {
      login(input: {email: $email, password: $password}) {
        ... on LoginMutationSuccess {
          token
        }
        ... on MutationError {
          errors
        }
      }
    }
'''
logout_mutation = '''
    mutation LogoutUser {
      logout(input: {}) {
        ... on LogoutMutationSuccess {
          loggedOut
        }
        ... on MutationError {
          errors
        }
      }
    }
'''


@pytest.fixture
def new_user(db):
    def create_user(name, gender):
        first_name, last_name = name.rsplit(maxsplit=1)
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=f'{first_name}@email.com',
            password=bcrypt.generate_password_hash(password).decode(),
            gender=gender,
        )
        db.session.add(user)
        db.session.commit()
        return user
    return create_user


def test__Login__pass(new_user):
    amy = new_user('amy ponds', Gender.FEMALE)

    resp = client.execute(
        login_mutation,
        variable_values={'email': amy.email, 'password': password}
    )

    payload = verify_token(resp['data']['login']['token'])
    assert payload['sub'] == amy.id


def test__Login__fail_incorrect_email(new_user, snapshot):
    rory = new_user('rory williams', Gender.MALE)
    snapshot.assert_match(client.execute(login_mutation, variable_values={
        'email': 'incorrect' + rory.email, 'password': password
    }))


def test__Login__fail_incorrect_password(new_user, snapshot):
    doctor = new_user('doctor who', Gender.OTHERS)
    snapshot.assert_match(client.execute(login_mutation, variable_values={
        'email': doctor.email, 'password': 'incorrect' + password
    }))


def test__Logout__pass(app, db, snapshot):
    bill_id = 4
    token = get_new_token(bill_id)

    with app.test_request_context(
            headers={'Authorization': f'Bearer {token}'}):
        snapshot.assert_match(client.execute(logout_mutation))

    payload = verify_token(token)
    assert BlacklistToken.query.get(payload['jti']) is not None


def test__Logout__pass_expired_token(app, db, snapshot):
    rory_id = 1

    # expired token
    current_app.config['JWT_EXP_SEC'] = 0
    token = get_new_token(rory_id)
    current_app.config['JWT_EXP_SEC'] = 60 * 60

    with app.test_request_context(
            headers={'Authorization': f'Bearer {token}'}):
        snapshot.assert_match(client.execute(logout_mutation))


def test__Logout__fail_invalid_token(app, db, snapshot):
    song_id = 5
    token = get_new_token(song_id)

    with app.test_request_context(
            headers={'Authorization': f'Bearer invalid_{token}'}):
        snapshot.assert_match(client.execute(logout_mutation))


def test__Logout__fail_blacklist_token(app, db, snapshot):
    amy_id = 5
    token = get_new_token(amy_id)

    with app.test_request_context(
            headers={'Authorization': f'Bearer {token}'}):
        snapshot.assert_match(client.execute(logout_mutation))
        snapshot.assert_match(client.execute(logout_mutation))


def test__Logout__fail_no_token_included(app, snapshot):
    with app.test_request_context(headers={'Authorization': ''}):
        snapshot.assert_match(client.execute(logout_mutation))


def test__Logout__fail_no_auth_header_included(app, snapshot):
    with app.test_request_context():
        snapshot.assert_match(client.execute(logout_mutation))
