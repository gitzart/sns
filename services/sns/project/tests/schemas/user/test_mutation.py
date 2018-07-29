import jwt

from flask import current_app
from graphene import test
from graphql_relay import to_global_id

from project.api.models.user import User
from project.api.schemas import schema
from project.api.schemas.user.query import UserType


client = test.Client(schema)


def test__CreateUser__pass(db, snapshot):
    mutation = '''
        mutation NewUser {
          createUser(input: {
            firstName: "    роРи "
            lastName: "wIllIamS     "
            email: "rory@русски4ever.орг"
            password: "рори's passw0rd"
            gender: MALE
            birthday: "1985-01-01"
          }) {
            __typename
            ... on UserMutationSuccess {
              token
              user {
                id
                name
                email
                gender
                birthday
              }
            }
            ... on MutationError {
              errors
            }
          }
        }
    '''
    resp = client.execute(mutation)
    token = resp['data']['createUser'].pop('token')
    snapshot.assert_match(resp)

    payload = jwt.decode(
        token,
        current_app.config['SECRET_KEY'],
        current_app.config['JWT_ALGO'],
    )
    rory_id = 1
    assert payload['sub'] == rory_id


def test__CreateUser__fail_input_validation(db, snapshot):
    mutation = '''
        mutation NewUser {
          createUser(input: {
            firstName: "the name amy should not be larger than fifty letters"
            lastName: "      "
            email: "amy@dash-at-the-end-"
            password: "contains ALT chars: √Ω"
            gender: FEMALE
            birthday: "1890-01-01"
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation))


def test__CreateUser__fail_email_uniqueness(setup, db, snapshot):
    mutation = '''
        mutation NewUser {
          createUser(input: {
            firstName: "doctor"
            lastName: "who"
            email: "doctor@email.com"
            password: "Doctor's passw0rd"
            gender: OTHERS
            birthday: "1900-01-01"
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation))


def test__UpdateUser__pass(setup, db, snapshot):
    id = to_global_id(UserType.__name__, 5)

    mutation = '''
        mutation UserToUpdate ($id: ID!) {
          updateUser(input: {
            id: $id
            lastName: "who"
            username: "melodywho"
            bio: "Doctor's mine now, bitches!"
            maritalStatus: MARRIED
          }) {
            __typename
            ... on UserMutationSuccess {
              user {
                id
                name
                username
                bio
                maritalStatus
              }
            }
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={'id': id}))


def test__UpdateUser__fail_invalid_ID(db, snapshot):
    id = to_global_id(UserType.__name__, 'invalid')

    mutation = '''
        mutation UserToUpdate ($id: ID!) {
          updateUser(input: {
            id: $id
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={'id': id}))


def test__UpdateUser__fail_user_existence(db, snapshot):
    id = to_global_id(UserType.__name__, 100)

    mutation = '''
        mutation UserToUpdate ($id: ID!) {
          updateUser(input: {
            id: $id
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={'id': id}))


def test__UpdateUser__fail_input_validation(setup, db, snapshot):
    id = to_global_id(UserType.__name__, 1)

    mutation = '''
        mutation UserToUpdate ($id: ID!) {
          updateUser(input: {
            id: $id
            username: ".dotAtTheBeginning"
            bio: "I was once a Centurion."
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={'id': id}))


def test__UpdateUser__fail_username_uniqueness(setup, db, snapshot):
    id = to_global_id(UserType.__name__, 3)

    song = User.query.get(5)
    song.username = 'timelord'
    db.session.commit()

    mutation = '''
        mutation UserToUpdate ($id: ID!) {
          updateUser(input: {
            id: $id
            username: "timelord"
          }) {
            __typename
            ... on MutationError {
              errors
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={'id': id}))
