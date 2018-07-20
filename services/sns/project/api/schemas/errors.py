import graphene


class MutationError(graphene.ObjectType):
    """Represent errors and constraints that occurred while `mutating` data.

    E.g. Input validation constraints, duplicate data error and etc.
    """

    errors = graphene.JSONString(
        required=True,
        description='JSON formatted error messages.'
    )
    client_mutation_id = graphene.Field(graphene.String)
