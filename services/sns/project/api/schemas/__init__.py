import graphene

from project.api.schemas.errors import MutationError
from project.api.schemas.user.query import Query as UserQuery
from project.api.schemas.auth.mutation import (
    Mutation as LoginMutation,
    LoginMutationSuccess,
)
from project.api.schemas.user.mutation import (
    Mutation as UserMutation,
    UserMutationSuccess,
)


class Query(UserQuery, graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(LoginMutation, UserMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query, mutation=Mutation,
    types=[MutationError, LoginMutationSuccess, UserMutationSuccess]
)
