from graphene.test import Client

from graphql_relay import to_global_id

from project.api.models.enums import Gender
from project.api.models.user import User
from project.api.schemas.schema import schema


client = Client(schema)


def test_mutation_user_create(db, snapshot):
    query = '''
        mutation NewUser {
          createUser(input: {
            firstName: "rory"
            lastName: "williams"
            email: "rory@email.com"
            gender: MALE
            password: "roryspassword"
          }) {
            user {
              id
              firstName
              lastName
              email
              gender
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(query))


def test_mutation_user_update(db, snapshot):
    id = to_global_id('User', 1)

    user = User(
        first_name='amy',
        last_name='pond',
        email='amy@email.com',
        gender=Gender.FEMALE,
        password='amyspassword'
    )
    db.session.add(user)
    db.session.commit()

    query = '''
        mutation UpdatedUser($id: ID!) {
          updateUser(input: {
            id: $id
            lastName: "williams"
            username: "amy"
            maritalStatus: MARRIED
          }) {
            user {
              id
              firstName
              lastName
              email
              gender
              username
              maritalStatus
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))
