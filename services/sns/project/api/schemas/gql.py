import graphene

from sqlalchemy.orm.query import Query as SQLAlchemyQuery
from graphene import relay
from graphql_relay.connection.arrayconnection import connection_from_list_slice


def connection_factory(node, name=None):
    """Generate a Relay Connection.

    :param node: ObjectType class.
    :param name: Connection name.
    """

    class Connection(relay.Connection, node=node, name=name):
        total_count = graphene.Int(
            description='The total count of items in the connection.'
        )

        def resolve_total_count(connection, info):
            return connection.length

    return Connection


class ConnectionField(relay.ConnectionField):
    @classmethod
    def connection_resolver(cls, resolver, connection, root, info, **kwargs):
        iterable = resolver(root, info, **kwargs)

        if isinstance(iterable, SQLAlchemyQuery):
            _len = iterable.count()
        else:
            _len = len(iterable)

        connection = connection_from_list_slice(
            iterable,
            kwargs,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection,
            pageinfo_type=relay.connection.PageInfo,
            edge_type=connection.Edge
        )
        connection.iterable = iterable
        connection.length = _len
        return connection
