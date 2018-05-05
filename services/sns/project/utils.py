import re

import graphene

from project import db


def to_gql_enum(py_enum):
    """Convert Python enumeration into GraphQL enumeration."""

    def description(enum_member):
        if enum_member is not None:
            return enum_member.describe()
        return py_enum.__doc__

    return graphene.Enum.from_enum(py_enum, description=description)


def to_sa_enum(py_enum):
    """Convert Python enumeration into SQLAlchemy enumeration."""
    return db.Enum(
        py_enum,
        name=to_snake_case(py_enum.__name__),
        values_callable=lambda x: [e.value for e in x],
    )


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(camel_str):
    """Convert CamelCase or mixedCase into snake_case."""
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()
