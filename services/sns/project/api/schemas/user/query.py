from ast import literal_eval

import graphene

from graphene import relay

from project import db
from project.api.models.enums import FriendshipState
from project.api.models.user import Friendship, User
from project.api.schemas.enums import Gender, MaritalStatus
from project.api.schemas.gql import connection_factory, ConnectionField


ACCEPTED, BLOCKED, PENDING, SUGGESTED = FriendshipState.__members__.values()


class UserType(graphene.ObjectType, interfaces=(relay.Node,)):
    """A user represents a person."""

    created_at = graphene.DateTime(
        description='Time when the user signed up.'
    )
    updated_at = graphene.DateTime(
        description='Time when the user profile was updated.'
    )
    first_name = graphene.String(
        description="The user's first name."
    )
    last_name = graphene.String(
        description="The user's last name."
    )
    name = graphene.String(
        description="The user's full name."
    )
    email = graphene.String(
        description="The user's primary email address listed on their profile."
    )
    username = graphene.String(
        description='Unique username. Can be used as part of the profile URL.'
    )
    birthday = graphene.Date(
        description="The user's birthday."
    )
    bio = graphene.String(
        description="The user's short biography."
    )
    gender = Gender(
        description="The gender selected by this user."
    )
    marital_status = MaritalStatus(
        description="The user's relationship status."
    )
    friends = ConnectionField(
        lambda: UserConnection,
        description="The user's friends."
    )
    blocked_users = ConnectionField(
        lambda: UserConnection,
        description='People who the user has blocked.'
    )
    followers = ConnectionField(
        lambda: UserConnection,
        description='People who are following the user.'
    )
    followings = ConnectionField(
        lambda: UserConnection,
        description='People who the user is following.'
    )
    friend_requests = ConnectionField(
        lambda: FriendRequestConnection,
        description='Friend requests (Inbox and outbox) of the user.'
    )
    friend_suggestions = ConnectionField(
        lambda: FriendSuggestionConnection,
        description='Friend suggestions (Inbox and outbox) of the user.'
    )

    @classmethod
    def get_node(cls, info, id):
        return User.query.get(id)

    def resolve_name(obj, info, **kwargs):
        return f'{obj.first_name} {obj.last_name}'

    def resolve_friends(obj, info, **kwargs):
        return obj.friendship.filter(Friendship.state == ACCEPTED)

    def resolve_blocked_users(obj, info, **kwargs):
        return obj.friendship.filter(
            Friendship.state == BLOCKED, Friendship.action_user_id == obj.id)

    def resolve_followers(obj, info, **kwargs):
        return obj.followers

    def resolve_followings(obj, info, **kwargs):
        return obj.followings

    def resolve_friend_requests(obj, info, **kwargs):
        subquery = (
            Friendship.query.filter_by(state=PENDING, left_user_id=obj.id).
            subquery(Friendship.__tablename__)
        )
        q = (
            db.session.query(User, subquery).
            join(subquery, subquery.c.right_user_id == User.id).
            order_by(Friendship.updated_at.desc())
        )

        iterable = []
        for row in q:
            if row.action_user_id == obj.id:
                sender, receiver = obj, row.User
            else:
                receiver, sender = obj, row.User

            iterable.append(FriendRequestType(
                id=(sender.id, receiver.id),
                sender=sender, receiver=receiver,
                created_at=row.updated_at
            ))
        return iterable

    # REVIEW: Join VS multiple quries
    #
    # Not sure which one is better. In JOIN case, query returns
    # repeated data. See the commit 1b35f19.
    #
    # In multiple-query case, query might be slow
    # and there is Python looping overhead. However, if suggestions
    # were limited to 5000 records, the overhead wouldn't
    # be a problem.
    #
    def resolve_friend_suggestions(obj, info, **kwargs):
        lt_exprs = Friendship.left_user_id < Friendship.right_user_id
        or_exprs = db.or_(
            Friendship.left_user_id == obj.id,
            Friendship.right_user_id == obj.id,
            Friendship.action_user_id == obj.id,
        )
        suggestions = (
            Friendship.query.
            filter(Friendship.state == SUGGESTED, lt_exprs, or_exprs).
            order_by(Friendship.updated_at.desc()).
            all()
        )

        # Collect unique IDs to get users by
        ids = set()
        for s in suggestions:
            ids.update({s.left_user_id, s.right_user_id, s.action_user_id})

        q = User.query.filter(User.id.in_(ids))
        users = {u.id: u for u in q.all()}

        iterable = []
        for s in suggestions:
            lid = s.left_user_id
            rid = s.right_user_id
            aid = s.action_user_id

            iterable.append(FriendSuggestionType(
                id=(lid, rid, aid),
                suggester=users[aid],
                receivers=[users[lid], users[rid]],
                created_at=s.updated_at
            ))
        return iterable


class FriendRequestType(graphene.ObjectType, interfaces=(relay.Node,)):
    sender = graphene.Field(
        UserType,
        name='from',
        description='The person who sent the request.'
    )
    receiver = graphene.Field(
        UserType,
        name='to',
        description='The person who received the request.'
    )
    created_at = graphene.DateTime(
        description='Time when the request was created.'
    )

    @classmethod
    def get_node(cls, info, id):
        lid, rid = literal_eval(id)

        request = (
            Friendship.query.
            filter_by(state=PENDING, left_user_id=lid, right_user_id=rid).
            first()
        )
        if request is None:
            raise Exception('Friend request not found.')

        users = User.query.filter(User.id.in_([lid, rid])).all()

        if request.action_user_id == users[0].id:
            sender, receiver = users
        else:
            receiver, sender = users

        return cls(
            id=id, sender=sender, receiver=receiver,
            created_at=request.updated_at
        )


class FriendSuggestionType(graphene.ObjectType, interfaces=(relay.Node,)):
    suggester = graphene.Field(
        UserType,
        name='from',
        description='The person who suggested the friendship.'
    )
    receivers = graphene.List(
        UserType,
        name='to',
        description='2 people who received the suggestion.'
    )
    created_at = graphene.DateTime(
        description='Time when the suggestion was created.'
    )

    @classmethod
    def get_node(cls, info, id):
        lid, rid, aid = literal_eval(id)

        suggestion = (
            Friendship.query.
            filter_by(state=SUGGESTED, left_user_id=lid).
            filter_by(right_user_id=rid, action_user_id=aid).
            first()
        )
        if suggestion is None:
            raise Exception('Friend suggestion not found.')

        users = User.query.filter(User.id.in_((lid, rid, aid))).all()

        for i, u in enumerate(users):
            if suggestion.action_user_id == u.id:
                suggester = users.pop(i)
                break

        return cls(
            id=id, suggester=suggester, receivers=users,
            created_at=suggestion.updated_at
        )


UserConnection = connection_factory(
    UserType, 'UserConnection'
)
FriendRequestConnection = connection_factory(
    FriendRequestType, 'FriendRequestConnection'
)
FriendSuggestionConnection = connection_factory(
    FriendSuggestionType, 'FriendSuggestionConnection'
)


class Query(graphene.ObjectType):
    user = relay.Node.Field(UserType)
