import re

from datetime import date, datetime, timedelta

import graphene
import jwt

from flask import current_app
from graphql_relay import from_global_id
from sqlalchemy.exc import IntegrityError

from project import bcrypt, db
from project.api.models.user import User
from project.api.schemas.enums import Gender, MaritalStatus
from project.api.schemas.errors import MutationError
from project.api.schemas.user.query import UserType
from project.api.schemas.validator import Validator
from project.utils import format_name


special_chars = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"

v_schema = {
    'first_name': {
        'type': 'string',
        'allspace': False,
        'regex': '^((?![\d_])[\w ]){1,50}$',
    },
    'last_name': {
        'type': 'string',
        'allspace': False,
        'regex': '^((?![\d_])[\w ]){1,50}$',
    },
    'email': {
        'type': 'string',
        'allspace': False,
        'validator': 'email',
    },
    'password': {
        'type': 'string',
        'allspace': False,
        'regex': '^[\w%s]{6,}$' % re.escape(special_chars),
    },
    'birthday': {
        'type': 'date',
        'min': date(year=date.today().year - 120, month=1, day=1),
        'max': date.today(),
    },
    'username': {
        'type': 'string',
        'validator': 'username',
    }
}
v_user = Validator(v_schema, allow_unknown=True)


class UserMutationSuccess(graphene.ObjectType):
    """Return User obj when the mutation is a success."""

    user = graphene.Field(
        UserType,
        required=True,
        description='The mutated user.'
    )
    token = graphene.String(description='A new JSON web token.')
    client_mutation_id = graphene.String()


class UserMutationPayload(graphene.Union):
    class Meta:
        types = (MutationError, UserMutationSuccess)


class CreateUser(graphene.relay.ClientIDMutation):
    Output = UserMutationPayload

    class Input:
        first_name = graphene.String(
            required=True,
            description="The user's first name."
        )
        last_name = graphene.String(
            required=True,
            description="The user's last name."
        )
        email = graphene.String(
            required=True,
            description="The user's primary email address."
        )
        password = graphene.String(
            required=True,
            description="Account password."
        )
        birthday = graphene.Date(
            required=True,
            description="The user's birthday."
        )
        gender = Gender(
            required=True,
            description="The gender selected by this user."
        )

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        input.pop('client_mutation_id', None)

        # Validate user input
        if not v_user.validate(input):
            return MutationError(errors=v_user.errors)

        # Check email uniqueness
        user = User.query.filter_by(email=input['email']).first()
        if user is not None:
            d = {'email': 'email address already exists'}
            return MutationError(errors=d)

        # TODO: Send a confirmation email

        # Format the names
        for k in ['first_name', 'last_name']:
            input[k] = format_name(input[k])

        # Hash password
        password = bcrypt.generate_password_hash(input['password']).decode()
        input['password'] = password
        user = User(**input)

        # Persist to db
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return MutationError(errors={'db': e.args[0]})

        # Issue a new JSON token
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'exp': now + timedelta(seconds=current_app.config['JWT_EXP_SEC']),
            'sub': user.id,
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm=current_app.config['JWT_ALGO']
        ).decode()

        return UserMutationSuccess(user=user, token=token)


# TODO: Update email and password
class UpdateUser(graphene.relay.ClientIDMutation):
    Output = UserMutationPayload

    class Input:
        id = graphene.ID(
            required=True,
            description='The User ID to update.'
        )
        first_name = graphene.String(
            description="The user's first name."
        )
        last_name = graphene.String(
            description="The user's last name."
        )
        birthday = graphene.Date(
            description="The user's birthday."
        )
        gender = Gender(
            description="The gender selected by this user."
        )
        bio = graphene.String(
            description="The user's short biography."
        )
        marital_status = MaritalStatus(
            description="The user's relationship status."
        )
        username = graphene.String(
            description='Unique username.'
        )

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, **input):
        # Verify ID
        try:
            id = int(from_global_id(id)[1])
        except ValueError:
            return MutationError(errors={'id': 'invalid ID'})

        # Validate user input
        if not v_user.validate(input):
            return MutationError(errors=v_user.errors)

        # Check user existence
        user = User.query.get(id)
        if user is None:
            d = {'id': 'user with the given ID does not exist'}
            return MutationError(errors=d)

        # Check username uniqueness
        if input.get('username'):
            u = User.query.filter_by(username=input['username']).first()
            if u is not None and u.id != id:
                d = {'username': 'username already exists'}
                return MutationError(errors=d)

        # Update user instance
        for k, v in input.items():
            if k in ['first_name', 'last_name']:
                v = format_name(v)
            setattr(user, k, v)

        # Persist to db
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return MutationError(errors={'db': e.args[0]})

        return UserMutationSuccess(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field(description='Create a new user.')
    update_user = UpdateUser.Field(description='Update a user.')
