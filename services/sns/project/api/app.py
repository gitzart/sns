from flask import Blueprint
from flask_graphql import GraphQLView

from project.api.schemas import schema


sns_blueprint = Blueprint('sns', __name__)

sns_blueprint.add_url_rule(
    '/',
    view_func=GraphQLView.as_view(
        'graphql', schema=schema, graphiql=True
    )
)
