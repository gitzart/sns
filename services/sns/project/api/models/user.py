from datetime import datetime, timedelta

from project import db
from project.utils import to_sa_enum
from .enums import FriendshipState, Gender, MaritalStatus


SAFriendshipState = to_sa_enum(FriendshipState)
SAGender = to_sa_enum(Gender)
SAMaritalStatus = to_sa_enum(MaritalStatus)


ACCEPTED, BLOCKED, PENDING, SUGGESTED = FriendshipState.__members__.values()


class Friendship(db.Model):
    """Builds ``bi-directional`` friendship between two users."""

    __tablename__ = 'friendships'

    __table_args__ = (db.CheckConstraint('left_user_id <> right_user_id'),)

    left_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    right_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    action_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    state = db.Column(SAFriendshipState, nullable=False)

    created = db.Column(db.DateTime)

    left_user = db.relationship(
        'User',
        foreign_keys=left_user_id,
        backref=db.backref('right_users', cascade='all, delete-orphan')
    )

    right_user = db.relationship(
        'User',
        foreign_keys=right_user_id,
        backref=db.backref('left_users', cascade='all, delete-orphan')
    )

    action_user = db.relationship(
        'User',
        foreign_keys=action_user_id
    )

    def __init__(self, n1, n2, action_user, state, created=None):
        self.left_user = n1
        self.right_user = n2
        self.action_user = action_user
        self.state = state
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<{} {}, {}>'.format(
            self.__class__.__name__,
            self.left_user.name,
            self.right_user.name,
        )

    @classmethod
    def get(cls, n1, n2):
        """Helper method whose function is different from
        from SQLAlchemy Query method ``get()``.

        Get mutual instances based on the given composite primary key,
        together with additional filtering criteria, if given.

        For example, to see if user A and B has blocked each other::

            Friendship.get(A, B).filter_by(type='block'). \
                count() > 0
        """

        return cls.query.filter(db.or_(
            db.and_(cls.left_user == n1, cls.right_user == n2),
            db.and_(cls.left_user == n2, cls.right_user == n1)
        ))

    @classmethod
    def build(cls, n1, n2, action_user, state):
        created = datetime.utcnow()
        return (cls(n1, n2, action_user, state, created),
                cls(n2, n1, action_user, state, created))

    @classmethod
    def update(cls, n1, n2, action_user, state, lazy=False):
        """
        :param lazy: When True, a new relationship will be built
            if not already existed.
        """
        rv = cls.get(n1, n2).all()

        if rv:
            r1, r2 = rv
            r1.created = r2.created = datetime.utcnow()
            r1.action_user = r2.action_user = action_user
            r1.state = r2.state = state
            return r1, r2

        if lazy:
            return cls.build(n1, n2, action_user, state)

    @classmethod
    def destroy(cls, n1, n2):
        return cls.get(n1, n2).delete(synchronize_session=False)


class Follower(db.Model):
    """Builds ``uni or bi-directional`` following and follower
    relationships.
    """

    __tablename__ = 'followers'

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    expiration = db.Column(db.DateTime)
    created = db.Column(db.DateTime)

    follower = db.relationship(
        'User',
        foreign_keys=follower_id,
        backref=db.backref('followed_users', cascade='all, delete-orphan')
    )

    followed = db.relationship(
        'User',
        foreign_keys=followed_id,
        backref=db.backref('follower_users', cascade='all, delete-orphan')
    )

    def __init__(self, follower, followed, expiration=None, create=None):
        self.follower = follower
        self.followed = followed
        self.expiration = expiration
        self.created = create or datetime.utcnow()

    def __repr__(self):
        return '<{} {}, {}>'.format(
            self.__class__.__name__,
            self.follower.name,
            self.followed.name,
        )

    @classmethod
    def get(cls, follower, followed, mutual=False):
        """Helper method whose function is different from
        from SQLAlchemy Query method ``get()``.

        Get a single instance or mutual instances based on
        the given follower and followed composite primary key,
        together with additional filtering criteria, if given.

        For example, to find an unexpired snoozed relationship
        of the follower::

            Follower.get(follower, followed). \
                filter(Follower.expiration > datetime.utcnow()). \
                first()

        :param mutual: Set it to True to find the relationship
            from both sides.
        """
        if mutual:
            return cls.query.filter(db.or_(
                db.and_(cls.follower == follower, cls.followed == followed),
                db.and_(cls.follower == followed, cls.followed == follower)
            ))
        else:
            return cls.query.filter(db.and_(
                cls.follower == follower,
                cls.followed == followed,
            ))

    @classmethod
    def build(cls, follower, followed, expiration=None, mutual=False):
        """
        :param mutual: When True, relationship will be built mutually.
        """
        if mutual:
            return (cls(follower, followed, expiration),
                    cls(followed, follower, expiration))
        else:
            return cls(follower, followed, expiration)

    @classmethod
    def update(cls, follower, followed, expiration=None, mutual=False, lazy=False):
        """
        :param mutual: When True, relationship will be updated mutually.

        :param lazy: When True, a new relationship will be built
            if not already existed.
        """
        if mutual:
            rv = cls.get(follower, followed, mutual=True).all()
        else:
            rv = cls.query.get((follower.id, followed.id))

        if rv:
            try:
                r1, r2 = rv
            except TypeError:
                # ignore when parameter ``mutual`` is False
                # and there is only one relationship
                pass
            except ValueError:
                # raise when parameter ``mutual`` is True
                e = (
                    'need bi-directional relationship to unpack, '
                    'but only one exists: {}'
                ).format(rv[0])
                raise ValueError(e) from None
            else:
                r1.expiration = r2.expiration = expiration
                return r1, r2

            # quite sure the relationship is one-way
            rv.expiration = expiration
            return rv

        if lazy:
            return cls.build(follower, followed, expiration, mutual)

    @classmethod
    def destroy(cls, follower, followed, mutual=False):
        return cls.get(follower, followed, mutual=mutual). \
            delete(synchronize_session=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(SAGender, nullable=False)
    username = db.Column(db.String, unique=True)
    created = db.Column(db.DateTime)
    birthday = db.Column(db.Date)
    bio = db.Column(db.String)
    current_city = db.Column(db.String)
    marital_status = db.Column(SAMaritalStatus)

    # read-only generic friendship query
    friendship = db.relationship(
        'User',
        secondary='friendships',
        primaryjoin='User.id == Friendship.left_user_id',
        secondaryjoin='User.id == Friendship.right_user_id',
        lazy='dynamic',
        viewonly=True
    )

    # read-only followings and followers queries
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

    def __init__(self, first_name, gender):
        self.first_name = first_name
        self.last_name = 'lovelace'
        self.email = f'{first_name}@email.com'
        self.password = 'secret'
        self.gender = gender or Gender.OTHERS
        self.created = datetime.utcnow()

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            self.first_name,
        )

    @property
    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def friends(self):
        return self.friendship.filter(Friendship.state == ACCEPTED)

    @staticmethod
    def mutual_friends(n1, n2):
        def criteria(arg):
            return db.and_(
                Friendship.left_user == arg,
                Friendship.state == ACCEPTED
            )

        mutual_table = (
            db.select([(Friendship.right_user_id).label('id')]).
            where(criteria(n1)).
            intersect(
                db.select([(Friendship.right_user_id).label('id')]).
                where(criteria(n2))
            ).alias('mutual_relationships')
        )

        return User.query.join(mutual_table, User.id == mutual_table.c.id)

    def is_friend(self, n):
        return Friendship.get(self, n).filter_by(state=ACCEPTED).count() > 0

    def is_mutual_firend(self, n1, n2):
        return Friendship.query.filter(db.and_(
            Friendship.left_user == self,
            Friendship.state == ACCEPTED,
            db.or_(
                Friendship.right_user == n1,
                Friendship.right_user == n2
            )
        )).count() == 2

    def is_following(self, n):
        return Follower.query.get((self.id, n.id)) is not None

    def is_snoozing(self, n):
        return Follower.get(self, n).filter(
            Follower.expiration > datetime.utcnow()
        ).first() is not None

    def suggest(self, n1, n2):
        suggestible = Friendship.get(n1, n2).filter(db.or_(
            Friendship.state == ACCEPTED,
            Friendship.state == BLOCKED,
            Friendship.state == PENDING,
            Friendship.state == SUGGESTED,
        )).count() == 0

        if suggestible and self.is_mutual_firend(n1, n2):
            return Friendship.build(n1, n2, self, SUGGESTED)
        else:
            return None

    def make_friends(self, n):
        in_relationship = Friendship.get(self, n).filter(db.or_(
            Friendship.state == ACCEPTED,
            Friendship.state == BLOCKED,
            Friendship.state == PENDING,
        )).count() > 0

        if in_relationship:
            return None
        # update if friend suggestion exists, otherwise build
        return Friendship.update(self, n, self, PENDING, lazy=True)

    def accept(self, n):
        # the same user cannot make friend request and accept
        pending = Friendship.get(self, n).filter(db.and_(
            Friendship.state == PENDING,
            Friendship.action_user != self
        )).count() > 0

        if not pending:
            return None

        # follow each other
        Follower.update(self, n, mutual=True, lazy=True)

        return Friendship.update(self, n, self, ACCEPTED)

    def block(self, n):
        blocked = Friendship.get(self, n).filter_by(state=BLOCKED).count() > 0

        if blocked:
            return None

        # stop following each other
        Follower.destroy(self, n, mutual=True)

        # build if not in relationship, otherwise update
        return Friendship.update(self, n, self, BLOCKED, lazy=True)

    def unblock(self, n):
        # only the user who blocked can unblock
        blocked = Friendship.get(self, n).filter(
            Friendship.state == BLOCKED,
            Friendship.action_user == self
        ).count() > 0

        if not blocked:
            return None
        return Friendship.destroy(self, n)

    def unfriend(self, n):
        if not self.is_friend(n):
            return None
        return Friendship.destroy(self, n)

    def decline(self, n):
        pending = Friendship.get(self, n).filter_by(state=PENDING).count() > 0

        if not pending:
            return None
        return Friendship.destroy(self, n)

    def follow(self, n):
        if self.is_following(n):
            return None
        return Follower.build(self, n)

    def unfollow(self, n):
        if not self.is_following(n):
            return None
        return Follower.destroy(self, n)

    def snooze(self, n, days=30):
        if self.is_snoozing(n):
            return None

        if not self.is_following(n):
            return None

        expiration = datetime.utcnow() + timedelta(days=days)
        return Follower.update(self, n, expiration)

    def unsnooze(self, n):
        if not self.is_snoozing(n):
            return None
        return Follower.update(self, n, expiration=None)
