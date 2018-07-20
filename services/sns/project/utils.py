import re

import graphene

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from project import db


def format_name(name):
    """Strip spaces and format names.

    From ``  guiDO vAn    RoSSum`` to ``Guido van Rossum``.
    """
    try:
        name = ' '.join(c[0] + c[1:].lower() for c in name.split())
        return '{}{}'.format(name[0].upper(), name[1:])
    except (AttributeError, IndexError):
        pass


def order_by(query, model, props):
    """
    :param props: Properties (direction and field) to order query by.
    """
    if props:
        direction, field = props.values()
        field = getattr(model, field)
        direction = getattr(field, direction)
        return query.order_by(direction())
    return query


# From this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_case):
    components = snake_case.split('_')
    return components[0] + ''.join(c.capitalize() for c in components[1:])


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(camel_str):
    """Convert CamelCase or mixedCase into snake_case."""
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def to_gql_enum(py_enum):
    """Convert Python enumeration into GraphQL enumeration."""

    def description(enum_member):
        if enum_member is not None:
            return enum_member.value.describe()
        return py_enum.__doc__

    d = {
        '__doc__': py_enum.__doc__,
        'description': description,
    }

    for key, value in py_enum.__members__.items():
        d[key] = value

    return type(py_enum.__name__, (graphene.Enum,), d)


def to_sa_enum(py_enum):
    """Convert Python enumeration into SQLAlchemy enumeration."""
    return db.Enum(
        py_enum,
        name=to_snake_case(py_enum.__name__),
        values_callable=lambda x: [e.value for e in x],
    )


class utcnow(expression.FunctionElement):
    """SQLAlchemy UTC timestamp extension."""
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kwargs):
    """PostgreSQL timestamp syntax."""
    return "TIMEZONE('utc', statement_timestamp())"
