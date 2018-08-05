from datetime import datetime, timedelta

from project import db
from project.utils import to_sa_enum, utcnow
from project.api.models.enums import FriendshipState, Gender, MaritalStatus


SAFriendshipState = to_sa_enum(FriendshipState)
SAGender = to_sa_enum(Gender)
SAMaritalStatus = to_sa_enum(MaritalStatus)

ACCEPTED, BLOCKED, PENDING, SUGGESTED = FriendshipState.__members__.values()


class Friendship(db.Model):
    """Provide a mutual friendship for two people."""

    __tablename__ = 'friendships'

    __table_args__ = (db.CheckConstraint('left_user_id <> right_user_id'),)

    left_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    right_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    action_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, server_default=utcnow())
    updated_at = db.Column(
        db.DateTime, server_default=utcnow(), onupdate=utcnow()
    )
    state = db.Column(SAFriendshipState, nullable=False)

    left_user = db.relationship('User', foreign_keys=left_user_id)
    right_user = db.relationship('User', foreign_keys=right_user_id)
    action_user = db.relationship('User', foreign_keys=action_user_id)

    def __repr__(self):
        try:
            return '<{} {}, {}>'.format(
                self.__class__.__name__,
                self.left_user.first_name,
                self.right_user.first_name
            )
        except AttributeError:
            return super().__repr__()

    @classmethod
    def get(cls, id_1, id_2):
        """Given the composite primary key, return the query which
        finds the relationship of two people.
        """
        return cls.query.filter(db.or_(
            db.and_(cls.left_user_id == id_1, cls.right_user_id == id_2),
            db.and_(cls.left_user_id == id_2, cls.right_user_id == id_1)
        ))

    @classmethod
    def build(cls, id_1, id_2, id_3, state):
        """Build a mutual relationship."""
        return (
            cls(left_user_id=id_1, right_user_id=id_2, action_user_id=id_3,
                state=state),
            cls(left_user_id=id_2, right_user_id=id_1, action_user_id=id_3,
                state=state),
        )

    @staticmethod
    def update(iter, action_user_id, state):
        """
        :param iter: Iterable :class:`.Friendship` model instances.
        """
        for i in range(2):
            iter[i].action_user_id = action_user_id
            iter[i].state = state
        return iter

    @classmethod
    def delete(cls, id_1, id_2):
        """Remove the mutual relationship."""
        return cls.get(id_1, id_2).delete(synchronize_session=False)


class Follower(db.Model):
    """Provide a follower or following relationship."""

    __tablename__ = 'followers'

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    created_at = db.Column(db.DateTime, server_default=utcnow())
    updated_at = db.Column(
        db.DateTime, server_default=utcnow(), onupdate=utcnow()
    )
    is_snoozed = db.Column(db.Boolean, server_default='f')
    # Snooze timer expiration
    expiration = db.Column(db.DateTime)

    follower = db.relationship('User', foreign_keys=follower_id)
    followed = db.relationship('User', foreign_keys=followed_id)

    def __repr__(self):
        try:
            return '<{} {}, {}>'.format(
                self.__class__.__name__,
                self.follower.first_name,
                self.followed.first_name
            )
        except AttributeError:
            return super().__repr__()

    @classmethod
    def delete(cls, id_1, id_2):
        """Remove the relationship."""
        return cls.query.filter_by(
            follower_id=id_1, followed_id=id_2
        ).delete(synchronize_session=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=utcnow())
    updated_at = db.Column(
        db.DateTime, server_default=utcnow(), onupdate=utcnow()
    )
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(SAGender, nullable=False)
    username = db.Column(db.String, unique=True)
    birthday = db.Column(db.Date)
    bio = db.Column(db.Text)
    marital_status = db.Column(SAMaritalStatus)

    friendship = db.relationship(
        'User',
        secondary='friendships',
        primaryjoin='User.id == Friendship.left_user_id',
        secondaryjoin='User.id == Friendship.right_user_id',
        lazy='dynamic',
        viewonly=True
    )

    followers = db.relationship(
        'User',
        secondary='followers',
        primaryjoin='User.id == Follower.followed_id',
        secondaryjoin='User.id == Follower.follower_id',
        lazy='dynamic',
        viewonly=True,
        backref=db.backref('followings', lazy='dynamic')
    )

    posts = db.relationship(
        'Post',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='author'
    )

    comments = db.relationship(
        'Comment',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='author'
    )

    post_reactions = db.relationship(
        'PostReaction',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='actor'
    )

    comment_reactions = db.relationship(
        'CommentReaction',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='actor'
    )

    photos = db.relationship(
        'Photo',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='owner'
    )

    # photo albums the user created
    photo_albums = db.relationship(
        'PhotoAlbum',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='owner'
    )

    # photo albums the user contributes to
    associated_albums = db.relationship(
        'PhotoAlbumContribution',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='contributor'
    )

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            self.first_name
        )

    @classmethod
    def get_by_id(cls, id):
        try:
            id = int(id)
        except (TypeError, ValueError):
            raise Exception('invalid ID')
        return cls.query.get(id)

    @staticmethod
    def mutual_friends(id_1, id_2):
        """
        :return: :class:`.User` query
        """

        def criteria(id):
            return db.and_(
                Friendship.left_user_id == id,
                Friendship.state == ACCEPTED
            )

        mutual_table = (
            db.select([(Friendship.right_user_id).label('id')]).
            where(criteria(id_1)).
            intersect(
                db.select([(Friendship.right_user_id).label('id')]).
                where(criteria(id_2))
            ).alias('mutual_relationships')
        )

        return User.query.join(mutual_table, User.id == mutual_table.c.id)

    def is_friend(self, id):
        return (
            Friendship.get(self.id, id).filter_by(state=ACCEPTED).count() > 0
        )

    def is_following(self, id):
        return Follower.query.get((self.id, id)) is not None

    def is_mutual_firend_of(self, id_1, id_2):
        """Check if the viewer is the mutual friend of two people."""
        return (
            Friendship.query.
            filter_by(state=ACCEPTED, left_user_id=self.id).
            filter(Friendship.right_user_id.in_([id_1, id_2])).
            count() == 2
        )

    def suggest(self, id_1, id_2):
        """
        :return: Iterable :class:`.Friendship` instances
            if two people can be suggested, otherwise None.
        """
        suggestible = (
            Friendship.query.get((id_1, id_2)) is None and
            self.is_mutual_firend_of(id_1, id_2)
        )

        if not suggestible:
            return None
        return Friendship.build(id_1, id_2, self.id, SUGGESTED)

    def send_friend_request(self, id):
        """
        :return: Iterable :class:`.Friendship` instances
            if the request can be sent, otherwise None.
        """
        data = Friendship.get(self.id, id).all()

        if not data:
            return Friendship.build(self.id, id, self.id, PENDING)

        if data[0].state == SUGGESTED:
            return Friendship.update(data, self.id, PENDING)
        else:
            return None

    def accept(self, id):
        """
        :return: Iterable :class:`.Friendship` instances
            if the pending request can be accepted, otherwise None.
        """
        data = Friendship.get(self.id, id).all()

        if not data or data[0].state != PENDING:
            return None

        # The same person cannot make friend request and accept.
        if data[0].action_user_id == self.id:
            return None
        return Friendship.update(data, self.id, ACCEPTED)

    def block(self, id):
        """
        :return: Iterable :class:`.Friendship` instances
            if the viewer can block the other person, otherwise None.
        """
        data = Friendship.get(self.id, id).all()

        if not data:
            return Friendship.build(self.id, id, self.id, BLOCKED)

        # Blocked relationship already exists.
        if data[0].state == BLOCKED:
            return None
        return Friendship.update(data, self.id, BLOCKED)

    def unblock(self, id):
        """
        :return: Total count of deleted Friendship records or None.
        """
        data = Friendship.get(self.id, id).all()

        if not data or data[0].state != BLOCKED:
            return None

        # Only the blocker can unblock.
        if data[0].action_user_id == self.id:
            return Friendship.delete(self.id, id)
        else:
            return None

    def unfriend(self, id):
        """
        :return: Total count of deleted Friendship records or None.
        """
        if self.is_friend(id):
            return Friendship.delete(self.id, id)
        else:
            return None

    def decline_friend_request(self, id):
        """Decline or cancel the friend request.

        This function works for both sides. The request maker
        cancels the request or the receiver declines it.

        :return: Total count of deleted Friendship records or None.
        """
        data = Friendship.get(self.id, id).all()

        if data and data[0].state == PENDING:
            return Friendship.delete(self.id, id)
        else:
            return None

    def follow(self, id):
        """
        :return: :class:`.Follower` instance if the viewer can follow,
            otherwise None.
        """
        blocked = Friendship.get(self.id, id).filter_by(state=BLOCKED).all()

        if self.is_following(id) or blocked:
            return None
        return Follower(follower_id=self.id, followed_id=id)

    def unfollow(self, id):
        """
        :return: Total count of deleted Follower records or None.
        """
        if self.is_following(id):
            return Follower.delete(self.id, id)
        else:
            return None

    def snooze(self, id, days=30):
        """
        :return: :class:`.Follower` instance if the viewer can snooze,
            otherwise None.
        """
        data = Follower.query.get((self.id, id))

        if data is None or data.is_snoozed:
            return None

        data.expiration = datetime.utcnow() + timedelta(days=days)
        data.is_snoozed = True
        return data

    def unsnooze(self, id):
        """
        :return: :class:`.Follower` instance if the viewer can unsnooze,
            otherwise None.
        """
        data = Follower.query.get((self.id, id))

        if data is None or not data.is_snoozed:
            return None

        data.expiration = None
        data.is_snoozed = False
        return data
