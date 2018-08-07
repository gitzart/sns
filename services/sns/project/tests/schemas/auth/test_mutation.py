from flask import g
from graphene import test

from project.api.models.auth import get_new_token, verify_token
from project.api.models.user import User
from project.api.schemas import schema


client = test.Client(schema)
password = 'my_precious'


def test__Login__pass(setup, db):
    rory = User.get_by_id(1)
    mutation = '''
        mutation LoginUser($email: String!, $password: String!) {
          login(input: {email: $email, password: $password}) {
            token
          }
        }
    '''
    resp = client.execute(mutation, variable_values={
        'email': rory.email, 'password': password})
    assert isinstance(resp['data']['login']['token'], str)


def test__Login__fail_incorrect_credentials(db, snapshot):
    mutation = '''
        mutation LoginUser($email: String!, $password: String!) {
          login(input: {email: $email, password: $password}) {
            token
          }
        }
    '''
    snapshot.assert_match(client.execute(mutation, variable_values={
        'email': 'incorrect@email', 'password': 'incorrect password'}))


def test__Logout__pass(app_context, db, snapshot):
    token = get_new_token(1)
    payload = verify_token(token)
    g.payload = payload

    mutation = '''
        mutation LogoutUser {
          logout(input: {}) { ok }
        }
    '''
    snapshot.assert_match(client.execute(mutation))


def test__Logout__fail_login_required(app_context, snapshot):
    mutation = '''
        mutation LogoutUser {
          logout(input: {}) { ok }
        }
    '''
    snapshot.assert_match(client.execute(mutation))
