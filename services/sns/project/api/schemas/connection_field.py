from graphene import relay
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from sqlalchemy.orm.query import Query as SQLAlchemyQuery


# See the implementation of graphene_sqlalchemy library
# https://github.com/graphql-python/graphene-sqlalchemy/blob/master/graphene_sqlalchemy/fields.py  # noqa
class ConnectionField(relay.ConnectionField):
    @classmethod
    def connection_resolver(cls, resolver, connection, root, info, **args):
        iterable = resolver(root, info, **args)
        if isinstance(iterable, SQLAlchemyQuery):
            # TODO: revise the use of count() as some iterable are
            # joined SQLs and performance can be affected in that case.
            _len = iterable.count()
        else:
            _len = len(iterable)
        connection = connection_from_list_slice(
            iterable,
            args,
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
