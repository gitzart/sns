from graphene import test
from graphql_relay import to_global_id

from project.api.models.enums import FriendshipState
from project.api.models.user import Follower, Friendship
from project.api.schemas import schema


client = test.Client(schema)

ACCEPTED, BLOCKED, PENDING, SUGGESTED = FriendshipState.__members__.values()


def test_user_query_basic_profile(setup, snapshot):
    query = '''
        query BasicInfo($id: ID!) {
          user(id: $id) {
            id
            createdAt
            updatedAt
            firstName
            lastName
            email
            gender
            username
            birthday
            bio
            maritalStatus
          }
        }
    '''
    id = to_global_id('UserType', 1)
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_user_query_relationship_profile(setup, db, snapshot):
    db.session.add_all(Friendship.build(2, 3, 2, ACCEPTED))
    db.session.add_all(Friendship.build(2, 4, 2, ACCEPTED))
    db.session.add_all(Friendship.build(2, 5, 2, ACCEPTED))
    db.session.add_all(Friendship.build(2, 1, 2, BLOCKED))
    db.session.add(Follower(follower_id=2, followed_id=3))
    db.session.add(Follower(follower_id=2, followed_id=4))
    db.session.add(Follower(follower_id=2, followed_id=5))
    db.session.add(Follower(follower_id=1, followed_id=2))
    db.session.commit()

    query = '''
        query RelationshipInfo($id: ID!) {
          user(id: $id) {
            id
            name
            friends(first: 2) {
              ...edges
            }
            followers(first: 2) {
              ...edges
            }
            followings(first: 2) {
              ...edges
            }
            blockedUsers(first: 2) {
              ...edges
            }
          }
        }
        fragment edges on UserConnection {
          totalCount
          edges {
            node {
              id
              name
            }
          }
        }
    '''
    id = to_global_id('UserType', 2)
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_user_query_friend_requests(setup, db, snapshot):
    db.session.add_all(Friendship.build(3, 4, 3, PENDING))
    db.session.add_all(Friendship.build(3, 5, 3, PENDING))
    db.session.add_all(Friendship.build(3, 1, 1, PENDING))
    db.session.commit()

    query = '''
        query FriendRequest($id: ID!) {
          user(id: $id) {
            ...profile
            friendRequests(first: 5) {
              totalCount
              edges {
                node {
                  id
                  createdAt
                  to {
                    ...profile
                  }
                  from {
                    ...profile
                  }
                }
              }
            }
          }
        }
        fragment profile on UserType {
          id
          name
        }
    '''
    id = to_global_id('UserType', 3)
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))


def test_user_query_friend_suggestions(setup, db, snapshot):
    db.session.add_all(Friendship.build(4, 5, 1, SUGGESTED))
    db.session.add_all(Friendship.build(4, 2, 3, SUGGESTED))
    db.session.commit()

    query = '''
        query FriendSuggestion($id: ID!) {
          user(id: $id) {
            ...profile
            friendSuggestions(first: 5) {
              totalCount
              edges {
                node {
                  id
                  createdAt
                  to {
                    ...profile
                  }
                  from {
                    ...profile
                  }
                }
              }
            }
          }
        }
        fragment profile on UserType {
          id
          name
        }
    '''
    id = to_global_id('UserType', 4)
    snapshot.assert_match(client.execute(query, variable_values={'id': id}))
