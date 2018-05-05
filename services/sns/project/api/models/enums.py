from enum import Enum


class FriendshipState(Enum):
    """State of the user's friendship towards another users."""

    ACCEPTED = 'accepted'
    BLOCKED = 'blocked'
    PENDING = 'pending'
    SUGGESTED = 'suggested'

    def describe(self):
        d = {
            'accepted': 'The user has become a friend of another users.',
            'blocked': 'The user has blocked another users.',
            'pending': "The user's friend request is pending.",
            'suggested':
                "A friend of the user's has made a friend suggestion.",
        }
        return d[self.value]


class Gender(Enum):
    """The user's gender."""

    FEMALE = 'female'
    MALE = 'male'
    OTHERS = 'others'

    def describe(self):
        d = {
            'female': 'The user is a she.',
            'male': 'The user is a he.',
            'others': 'The user is anything: human, animal, plant and etc.',
        }
        return d[self.value]


class MaritalStatus(Enum):
    """Status of the user's romantic relationship."""

    CIVIL_UNION = 'civil union'
    COMPLICATED = 'complicated'
    DIVORCED = 'divorced'
    DOMESTIC_PARTNERSHIP = 'domestic partnership'
    MARRIED = 'married'
    OPEN_RELATIONSHIP = 'open relationship'
    SEPARATED = 'separated'
    SINGLE = 'single'
    TAKEN = 'taken'
    WIDOWED = 'widowed'

    def describe(self):
        return self.value


class Reaction(Enum):
    """The user's reaction to Posts and Comments."""

    ANGRY = 'angry'
    LAUGH = 'laugh'
    LIKE = 'like'
    LOVE = 'love'
    SAD = 'sad'
    WOW = 'wow'

    def describe(self):
        d = {
            'angry': 'Represents the 😡 emoji.',
            'laugh': 'Represents the 😂 emoji.',
            'like': 'Represents the 👍 emoji.',
            'love': 'Represents the ❤️ emoji.',
            'sad': 'Represents the 😢 emoji.',
            'wow': 'Represents the 😯 emoji.',
        }
        return d[self.value]
