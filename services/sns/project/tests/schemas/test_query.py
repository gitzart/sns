import pytest

from graphql_relay import to_global_id
from graphene.test import Client

from project.api.models.enums import FriendshipState, Gender
from project.api.models.user import Follower, Friendship, User
from project.api.schemas.schema import schema


client = Client(schema)


@pytest.fixture
def setup(db):
    users = [
        User(
            first_name='rory',
            last_name='williams',
            gender=Gender.MALE,
            email='rory@email.com',
            password='roryspassword'
        ),
        User(
            first_name='amy',
            last_name='pond',
            gender=Gender.FEMALE,
            email='amy@email.com',
            password='amyspassword'
        ),
        User(
            first_name='doctor',
            last_name='who',
            gender=Gender.OTHERS,
            email='doctor@email.com',
            password='doctorspassword'
        ),
        User(
            first_name='bill',
            last_name='potts',
            gender=Gender.FEMALE,
            email='bill@email.com',
            password='billspassword'
        ),
        User(
            first_name='song',
            last_name='river',
            gender=Gender.FEMALE,
            email='song@email.com',
            password='songspassword'
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    return users


def test_query_user_with_basic_info(setup, snapshot):
    id = to_global_id('User', 1)
    query = '''
        query BasicInfo($id: ID!) {
          user(id: $id) {
            firstName
            lastName
            gender
            email
            username
            bio
            birthday
            currentCity
            maritalStatus
          }
        }
    '''
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_query_user_with_relationship_info(setup, db, snapshot):
    id = to_global_id('User', 2)
    rory, amy = setup[:2]

    Friendship.build(rory, amy, amy, FriendshipState.ACCEPTED)
    Follower.build(rory, amy, mutual=True)
    db.session.commit()

    query = '''
        query RelationshipInfo($id: ID!) {
          user(id: $id) {
            firstName
            lastName
            friends {
              totalCount
              edges {
                node {
                  id
                  firstName
                  lastName
                }
              }
            }
            followers {
              totalCount
              edges {
                node {
                  id
                  firstName
                  lastName
                }
              }
            }
            followings {
              totalCount
              edges {
                node {
                  id
                  firstName
                  lastName
                }
              }
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_query_user_with_friend_request(setup, db, snapshot):
    id = to_global_id('User', 3)
    doctor, bill = setup[2:4]

    Friendship.build(doctor, bill, doctor, FriendshipState.PENDING)
    db.session.commit()

    query = '''
        query FriendRequest($id: ID!) {
          user(id: $id) {
            firstName
            lastName
            friendRequests(actionDirection: ALL) {
              totalCount
              edges {
                node {
                  id
                  to {
                    id
                    firstName
                    lastName
                  }
                  from {
                    id
                    firstName
                    lastName
                  }
                  message
                  unread
                }
              }
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_query_user_with_friend_suggestion(setup, db, snapshot):
    id = to_global_id('User', 4)
    doctor, bill, song = setup[2:]

    Friendship.build(doctor, song, doctor, FriendshipState.ACCEPTED)
    Friendship.build(doctor, bill, song, FriendshipState.SUGGESTED)
    db.session.commit()

    query = '''
        query FriendSuggestion($id: ID!) {
          user(id: $id) {
            firstName
            lastName
            friendSuggestions(actionDirection: ALL) {
              totalCount
              edges {
                node {
                  id
                  to {
                    id
                    firstName
                    lastName
                  }
                  from {
                    id
                    firstName
                    lastName
                  }
                  message
                  unread
                }
              }
            }
          }
        }
    '''
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))
