import graphene

from project import bcrypt
from project.api.models.auth import get_new_token, verify_token
from project.api.models.user import User
from project.api.schemas.errors import MutationError


class LoginMutationSuccess(graphene.ObjectType):
    """Return JWT token if the user has successfully logged in."""

    token = graphene.String(description='A new JSON web token.')
    client_mutation_id = graphene.String()


class LoginMutationPayload(graphene.Union):
    class Meta:
        types = (MutationError, LoginMutationSuccess)


class Login(graphene.relay.ClientIDMutation):
    Output = LoginMutationPayload

    class Input:
        email = graphene.String(
            required=True,
            description="The user's primary email address."
        )
        password = graphene.String(
            required=True,
            description='Account password.'
        )

    @classmethod
    def mutate_and_get_payload(cls, root, info, email, password, **input):
        error = MutationError(errors={'login': 'incorrect credentials'})

        if email.isspace() or len(email) == 0:
            return error

        user = User.query.filter_by(email=email).first()
        if user is None:
            return error

        correct_pass = bcrypt.check_password_hash(user.password, password)
        if not correct_pass:
            return error

        return LoginMutationSuccess(token=get_new_token(user.id))


class LogoutMutationSuccess(graphene.ObjectType):
    """Return Boolean value if the user has successfully logged out."""

    logged_out = graphene.Boolean()
    client_mutation_id = graphene.String()


class LogoutMutationPayload(graphene.Union):
    class Meta:
        types = (MutationError, LogoutMutationSuccess)


class Logout(graphene.relay.ClientIDMutation):
    Output = LogoutMutationPayload

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        # Get request header
        try:
            auth_header = info.context.get('Authorization')
        except AttributeError:
            auth_header = info.context.headers.get('Authorization')

        if not auth_header:
            return MutationError(errors={'logout': "you have not logged in"})

        # Decode the token
        payload = verify_token(auth_header.split()[1])
        if payload == 'invalid':
            return MutationError(errors={'logout': 'invalid token'})

        return LogoutMutationSuccess(logged_out=True)


class Mutation(graphene.ObjectType):
    login = Login.Field(description="Log in to the user's account.")
    logout = Logout.Field(description="Log out of the user's account.")
