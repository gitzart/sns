from enum import Enum


class FriendshipType(Enum):
    """Status of the friendship between two users."""

    BLOCKED = 'blocked'
    FRIENDED = 'friended'
    PENDING = 'pending'
    SUGGESTED = 'suggested'

    def describe(self):
        d = {
            'blocked': (
                'The relationship is blocked; '
                'the users cannot communicate each other.'
            ),
            'friended': (
                'The users are friends.'
            ),
            'pending': (
                'The friend request is pending.'
            ),
            'suggested': (
                'The friend suggestion is made by '
                'a mutual friend of both users.'
            ),
        }
        return d[self.value]


class Gender(Enum):
    """Gender of the user."""

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


class Reaction(Enum):
    """Raction of the user to posts and comments."""

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


class RelationshipStatus(Enum):
    """Status of the romantic relationship of the user."""

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
