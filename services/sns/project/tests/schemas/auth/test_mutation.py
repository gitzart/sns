import jwt

from flask import current_app
from graphene import test

from project import bcrypt
from project.api.models.enums import Gender
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
    token = jwt.decode(
        resp['data']['login']['token'],
        current_app.config['SECRET_KEY'],
        current_app.config['JWT_ALGO'],
    )
    assert token['sub'] == amy.id


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
