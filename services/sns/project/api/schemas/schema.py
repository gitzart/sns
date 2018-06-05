from ast import literal_eval

import graphene

from graphene import relay
from graphene.types.datetime import Date, DateTime
from graphql_relay import from_global_id
from sqlalchemy import exc
from sqlalchemy.dialects import postgresql

from project import bcrypt, db
from project.api.models.user import (
    Friendship as FriendshipModel,
    User as UserModel,
)
from project.api.schemas.enums import (
    ActionDirection,
    FriendshipState,
    Gender,
    MaritalStatus,
    OrderDirection,
    UserOrderField,
)
from project.utils import connection_factory, get_direction_func
from .connection_field import ConnectionField


class UserOrder(graphene.InputObjectType):
    """Ordering options for user connections."""

    direction = OrderDirection(
        required=True,
        description='The ordering direction.'
    )
    field = UserOrderField(
        required=True,
        description='The field to order users by.'
    )


class BasicUserFields(graphene.Interface):
    """The basic information of the user."""

    first_name = graphene.String(
        description='First name of the user.'
    )
    last_name = graphene.String(
        description='Last or family name of the user.'
    )
    email = graphene.String(
        description="The user's email which is used to log in."
    )
    username = graphene.String(
        description='Unique username. Used as part of the profile URL.'
    )
    birthday = Date(
        description="The user's birthday."
    )
    bio = graphene.String(
        description="The user's short biography."
    )
    current_city = graphene.String(
        description="The user's current location."
    )
    gender = Gender(
        description="Gender of the user."
    )
    marital_status = MaritalStatus(
        description="The user's romantic relationship status."
    )


class User(graphene.ObjectType):
    """An individual's account."""

    created = DateTime(
        name='createdTime',
        description='The user account creation date.'
    )
    friends = ConnectionField(
        lambda: UserConnection,
        description='Friends of the user.',
        order_by=graphene.Argument(UserOrder)
    )
    followers = ConnectionField(
        lambda: UserConnection,
        description='People who are following the user.',
        order_by=graphene.Argument(UserOrder)
    )
    followings = ConnectionField(
        lambda: UserConnection,
        description='People who the user is following.',
        order_by=graphene.Argument(UserOrder)
    )
    friend_requests = ConnectionField(
        lambda: FriendRequestConnection,
        description='Friend requests sent to or by the user.',
        indicator=ActionDirection(default_value=ActionDirection.INBOX.value)
    )
    friend_suggestions = ConnectionField(
        lambda: FriendSuggestionConnection,
        description='Friend suggestions made to or by the user.',
        indicator=ActionDirection(default_value=ActionDirection.INBOX.value)
    )
    blocked_users = ConnectionField(
        lambda: UserConnection,
        description='People who the user has blocked.',
        order_by=graphene.Argument(UserOrder)
    )

    class Meta:
        interfaces = (relay.Node, BasicUserFields)

    @classmethod
    def get_node(cls, info, id):
        return UserModel.query.get(id)

    def resolve_friends(instance, info, **kwargs):
        query = instance.friendship.filter(
            FriendshipModel.state == FriendshipState.ACCEPTED.value
        )

        if kwargs.get('order_by'):
            direction, field = kwargs['order_by'].values()
            direction = get_direction_func(direction)

            if field == UserOrderField.FULLNAME:
                criterion = (
                    direction(UserModel.first_name),
                    direction(UserModel.last_name),
                )
            else:
                criterion = (direction(getattr(UserModel, field)),)

            query = query.order_by(*criterion)

        return query

    def resolve_followers(instance, info, **kwargs):
        query = instance.followers

        if kwargs.get('order_by'):
            direction, field = kwargs['order_by'].values()
            direction = get_direction_func(direction)

            if field == UserOrderField.FULLNAME:
                criterion = (
                    direction(UserModel.first_name),
                    direction(UserModel.last_name),
                )
            else:
                criterion = (direction(getattr(UserModel, field)),)

            query = query.order_by(*criterion)

        return query

    def resolve_followings(instance, info, **kwargs):
        query = instance.followings

        if kwargs.get('order_by'):
            direction, field = kwargs['order_by'].values()
            direction = get_direction_func(direction)

            if field == UserOrderField.FULLNAME:
                criterion = (
                    direction(UserModel.first_name),
                    direction(UserModel.last_name),
                )
            else:
                criterion = (direction(getattr(UserModel, field)),)

            query = query.order_by(*criterion)

        return query

    def resolve_friend_requests(instance, info, **kwargs):
        friend_requests = []
        indicator = kwargs['indicator']
        subquery_base = FriendshipModel.query.filter_by(
            state=FriendshipState.PENDING.value,
            left_user_id=instance.id
        )

        if indicator == ActionDirection.INBOX:
            subquery = subquery_base.filter(
                FriendshipModel.action_user_id != instance.id
            )
        elif indicator == ActionDirection.OUTBOX:
            subquery = subquery_base.filter(
                FriendshipModel.action_user_id == instance.id
            )
        else:
            subquery = subquery_base

        subquery = subquery.subquery('friendships')
        query = db.session.query(UserModel, subquery).join(
            subquery, subquery.c.right_user_id == UserModel.id
        )

        for result in query:
            friendship = FriendshipModel.to_obj(result[1:])
            user = result[0]

            if user.id == friendship.action_user_id:
                receiver = instance
                sender = user
            else:
                receiver = user
                sender = instance

            friend_requests.append(FriendRequest(
                id=(receiver.id, sender.id),
                receiver=receiver,
                sender=sender,
                created=friendship.created,
                message=friendship.message,
                unread=friendship.unread
            ))

        return friend_requests

    def resolve_friend_suggestions(instance, info, **kwargs):
        friend_suggestions = []
        indicator = kwargs['indicator']
        subquery_base = FriendshipModel.query.filter_by(
            state=FriendshipState.SUGGESTED.value
        )

        if indicator == ActionDirection.INBOX:
            subquery = subquery_base.filter_by(left_user_id=instance.id)
        elif indicator == ActionDirection.OUTBOX:
            subquery = subquery_base.filter(
                FriendshipModel.action_user_id == instance.id,
                FriendshipModel.left_user_id < FriendshipModel.right_user_id
            )
        else:
            subquery = subquery_base.filter(db.or_(
                FriendshipModel.left_user_id == instance.id,
                FriendshipModel.right_user_id == instance.id,
                FriendshipModel.action_user_id == instance.id
            ),
                FriendshipModel.left_user_id < FriendshipModel.right_user_id
            )

        subquery = subquery.subquery('friendships')
        query = db.session.query(UserModel, subquery).join(subquery, db.or_(
            subquery.c.left_user_id == UserModel.id,
            subquery.c.right_user_id == UserModel.id,
            subquery.c.action_user_id == UserModel.id
        )).with_labels()

        # Use raw SQL to get data because ORM Query
        # cuts out the same obj for performance.
        # See https://stackoverflow.com/a/6934782
        plain_sql = query.statement.compile(dialect=postgresql.dialect())

        user_col_length = len(UserModel.__table__.columns)
        results = db.engine.execute(plain_sql).fetchall()
        step = 3

        for i in range(0, len(results), step):
            # to model objs from tuple values
            friendship = FriendshipModel.to_obj(results[i][user_col_length:])
            user = UserModel.to_obj(results[i][:user_col_length])
            user2 = UserModel.to_obj(results[i + 1][:user_col_length])
            user3 = UserModel.to_obj(results[i + 2][:user_col_length])

            if user.id == friendship.action_user_id:
                users = [user2, user3]
                suggester = user
            elif user2.id == friendship.action_user_id:
                users = [user, user3]
                suggester = user2
            else:
                users = [user, user2]
                suggester = user3

            friend_suggestions.append(FriendSuggestion(
                id=(users[0].id, users[1].id, suggester.id),
                users=users,
                suggester=suggester,
                created=friendship.created,
                message=friendship.message,
                unread=friendship.unread
            ))

        return friend_suggestions

    def resolve_blocked_users(instance, info, **kwargs):
        query = instance.friendship.filter(
            FriendshipModel.action_user_id == instance.id,
            FriendshipModel.state == FriendshipState.BLOCKED.value
        )

        if kwargs.get('order_by'):
            direction, field = kwargs['order_by'].values()
            direction = get_direction_func(direction)

            if field == UserOrderField.FULLNAME:
                criterion = (
                    direction(UserModel.first_name),
                    direction(UserModel.last_name),
                )
            else:
                criterion = (direction(getattr(UserModel, field)),)

            query = query.order_by(*criterion)

        return query


class FriendRequest(graphene.ObjectType, interfaces=(relay.Node,)):
    receiver = graphene.Field(
        User,
        name='to',
        description='The person to whom the friend request was sent.'
    )
    sender = graphene.Field(
        User,
        name='from',
        description='The person who sent the friend request.'
    )
    created = DateTime(
        name='createdTime',
        description='Time at which the friend request was created.'
    )
    message = graphene.String(
        description='Message provided by the sender when they sent the request.'
    )
    unread = graphene.Boolean(
        description='Whether the user has read the friend request or not.'
    )

    @classmethod
    def get_node(cls, info, id):
        receiver_id, sender_id = literal_eval(id)
        friendship = FriendshipModel.query.get((receiver_id, sender_id))
        users = UserModel.query.filter(db.or_(
            UserModel.id == receiver_id,
            UserModel.id == sender_id
        )).all()
        if users[0].id == receiver_id:
            receiver = users[0]
            sender = users[1]
        else:
            receiver = users[1]
            sender = users[0]
        return cls(
            id=id,
            receiver=receiver,
            sender=sender,
            created=friendship.created,
            message=friendship.message,
            unread=friendship.unread
        )


class FriendSuggestion(graphene.ObjectType, interfaces=(relay.Node,)):
    users = graphene.Field(
        graphene.List(User),
        name='to',
        description=(
            'The list of people to whom the friend suggestion was sent. '
            'The number of people is always 2.'
        )
    )
    suggester = graphene.Field(
        User,
        name='from',
        description='The person who suggested the friendship.'
    )
    created = DateTime(
        name='createdTime',
        description='Time at which the friend suggestion was created.'
    )
    message = graphene.String(
        description='Message provided by the sender when they sent the suggestion.'
    )
    unread = graphene.Boolean(
        description='Whether the user has read the friend suggestion or not.'
    )

    @classmethod
    def get_node(cls, info, id):
        user_id, user2_id, suggester_id = literal_eval(id)
        friendship = FriendshipModel.query.filter_by(
            left_user_id=user_id,
            right_user_id=user2_id,
            action_user_id=suggester_id
        ).first()
        users = UserModel.query.filter(db.or_(
            UserModel.id == user_id,
            UserModel.id == user2_id,
            UserModel.id == suggester_id,
        )).all()

        for i, user in enumerate(users):
            if user.id == suggester_id:
                suggester = users.pop(i)
                break

        return cls(
            id=id,
            users=users,
            suggester=suggester,
            created=friendship.created,
            message=friendship.message,
            unread=friendship.unread
        )


UserConnection = connection_factory(User)
FriendRequestConnection = connection_factory(FriendRequest)
FriendSuggestionConnection = connection_factory(FriendSuggestion)


class CreateUserInput:
    first_name = graphene.String(
        required=True,
        description='First name of the user.'
    )
    last_name = graphene.String(
        required=True,
        description='Last or family name of the user.'
    )
    email = graphene.String(
        required=True,
        description="The user's email which is used to log in."
    )
    password = graphene.String(
        required=True,
        description='User account password.'
    )
    gender = Gender(
        required=True,
        description="Gender of the user."
    )


class CreateUser(relay.ClientIDMutation):
    user = graphene.Field(User, description='The new user.')

    class Input(CreateUserInput):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        # Validate inputs
        for key, value in input.items():
            if isinstance(value, str) and not value.strip():
                raise Exception(f'{key} must be non-empty.')

        user = UserModel.query.filter_by(email=input['email']).first()
        if user is not None:
            raise Exception('email already exists.')

        password = input['password']
        input['password'] = bcrypt.generate_password_hash(password).decode()
        user = UserModel(**input)

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(e.args)

        return cls(user=user)


class UpdateUserInput(BasicUserFields):
    id = graphene.ID(
        required=True,
        description='The User ID to update.'
    )


class UpdateUser(relay.ClientIDMutation):
    user = graphene.Field(User, description='The updated user.')

    class Input(UpdateUserInput):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        non_empty_fields = ['first_name', 'last_name', 'email']

        # Validate inputs
        for field in non_empty_fields:
            value = input.get(field)
            if value is not None and not value.strip():
                raise Exception(f'{field} must be non-empty.')

        # Validate user ID
        _type, id = from_global_id(input.pop('id'))
        try:
            user = UserModel.query.get(id)
        except Exception as e:
            raise Exception('ID is not valid.')

        if user is not None:
            for key, value in input.items():
                setattr(user, key, value)
        else:
            raise Exception('User does not exist.')

        try:
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            raise Exception('email or username already exists.')

        return cls(user=user)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    user = relay.Node.Field(User)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field(description='Create a new user.')
    update_user = UpdateUser.Field(description='Update an existing user.')


schema = graphene.Schema(query=Query, mutation=Mutation)
