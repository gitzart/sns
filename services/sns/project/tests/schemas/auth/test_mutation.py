from flask import current_app
from graphene import test

from project import bcrypt
from project.api.models.enums import Gender
from project.api.models.auth import get_new_token, verify_token
from project.api.models.user import User
from project.api.schemas import schema


client = test.Client(schema)


def test__Login__pass(db):
    email = 'amy@email.com'
    password = 'my precious'
    amy = User(
        first_name='amy',
        last_name='ponds',
        email=email,
        password=bcrypt.generate_password_hash(password).decode(),
        gender=Gender.FEMALE,
    )
    db.session.add(amy)
    db.session.commit()

    mutation = '''
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

    resp = client.execute(mutation, variable_values={
        'email': email, 'password': password
    })
    payload = verify_token(resp['data']['login']['token'])
    assert payload['sub'] == amy.id


def test__Login__fail_incorrect_email(db, snapshot):
    email = 'rory@email.com'
    password = 'my precious'
    rory = User(
        first_name='rory',
        last_name='williams',
        email=email,
        password=bcrypt.generate_password_hash(password).decode(),
        gender=Gender.MALE,
    )
    db.session.add(rory)
    db.session.commit()

    mutation = '''
        mutation LoginUser($email: String!, $password: String!) {
          login(input: {email: $email, password: $password}) {
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={
        'email': 'incorrect' + email, 'password': password
    }))


def test__Login__fail_incorrect_password(db, snapshot):
    email = 'doctor@email.com'
    password = 'my precious'
    doctor = User(
        first_name='doctor',
        last_name='who',
        email=email,
        password=bcrypt.generate_password_hash(password).decode(),
        gender=Gender.OTHERS,
    )
    db.session.add(doctor)
    db.session.commit()

    mutation = '''
        mutation LoginUser($email: String!, $password: String!) {
          login(input: {email: $email, password: $password}) {
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={
        'email': email, 'password': 'incorrect' + password
    }))


def test__Logout__pass(db, snapshot):
    bill_id = 4
    token = get_new_token(bill_id)

    mutation = '''
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
    snapshot.assert_match(client.execute(mutation, context_value={
        'Authorization': f'Bearer {token}'
    }))


def test__Logout__pass_expired_token(db, snapshot):
    rory_id = 1

    # expired token
    current_app.config['JWT_EXP_SEC'] = 0
    token = get_new_token(rory_id)
    current_app.config['JWT_EXP_SEC'] = 60 * 60

    mutation = '''
        mutation LogoutUser {
          logout(input: {}) {
            ... on LogoutMutationSuccess {
              loggedOut
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, context_value={
        'Authorization': f'Bearer {token}'
    }))


def test__Logout__fail_invalid_token(db, snapshot):
    song_id = 5
    token = get_new_token(song_id)

    mutation = '''
        mutation LogoutUser {
          logout(input: {}) {
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, context_value={
        'Authorization': f'Bearer invalid_{token}'
    }))


def test__Logout__fail_no_token_included(db, snapshot):
    mutation = '''
        mutation LogoutUser {
          logout(input: {}) {
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, context_value={
        'Authorization': ''
    }))
