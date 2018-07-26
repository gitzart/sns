import graphene

from project import bcrypt
from project.api.models.auth import get_new_token
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


class Mutation(graphene.ObjectType):
    login = Login.Field(description="Log in to the user's account.")
