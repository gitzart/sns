import graphene

from project.api.models.auth import authenticate_password, logout


class Login(graphene.relay.ClientIDMutation):
    token = graphene.String(
        required=True,
        description='A new JSON web token.'
    )

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
        return cls(token=authenticate_password(email, password))


class Logout(graphene.relay.ClientIDMutation):
    ok = graphene.Boolean(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        return cls(ok=logout())


class Mutation(graphene.ObjectType):
    login = Login.Field(description="Log in to the user account.")
    logout = Logout.Field(description="Log out of the user account.")
