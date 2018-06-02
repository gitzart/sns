import graphene

from project.api.models.enums import (
    FriendshipState as _FriendshipState,
    Gender as _Gender,
    MaritalStatus as _MaritalStatus,
)
from project.utils import to_gql_enum


Gender = to_gql_enum(_Gender)

MaritalStatus = to_gql_enum(_MaritalStatus)

FriendshipState = to_gql_enum(_FriendshipState)


class ActionDirection(graphene.Enum):
    """Possible directions in which an action is made."""

    ALL = 'all'
    INBOX = 'inbox'
    OUTBOX = 'outbox'

    @property
    def description(self):
        d = {
            'all': 'Both inboxes and outboxes.',
            'inbox': 'An action is made to the user.',
            'outbox': 'The user made an action.',
        }
        return d.get(self.value)


class OrderDirection(graphene.Enum):
    """Possible directions in which to order a list of items
    when provided an ``orderBy`` argument.
    """

    ASC = 'asc'
    DESC = 'desc'

    @property
    def description(self):
        d = {
            'asc': 'Order a list of objects in an ascending order.',
            'desc': 'Order a list of objects in a descending order.',
        }
        return d.get(self.value)


class UserOrderField(graphene.Enum):
    """Properties by which user connections can be ordered."""

    BIRTHDAY = 'birthday'
    CREATED = 'created'
    FULLNAME = 'fullname'

    @property
    def description(self):
        d = {
            'birthday': 'Order a list of users by birthday.',
            'created': 'Order a list of users by creation time.',
            'fullname': 'Order a list of users by full name.',
        }
        return d.get(self.value)
