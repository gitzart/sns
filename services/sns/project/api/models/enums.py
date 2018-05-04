from enum import Enum

from project import db
from project.utils import to_snake_case


def to_sa_enum(py_enum):
    """Convert Python enumeration into SQLAlchemy enumeration."""
    return db.Enum(
        py_enum,
        name=to_snake_case(py_enum.__name__),
        values_callable=lambda x: [e.value for e in x],
    )


class FriendshipType(Enum):
    """Status of the friendship between two users."""

    FRIENDED = 'friended'
    PENDING = 'pending'
    BLOCKED = 'blocked'
    SUGGESTED = 'suggested'


class Gender(Enum):
    """Gender of the user."""

    MALE = 'male'
    FEMALE = 'female'
    OTHERS = 'others'
