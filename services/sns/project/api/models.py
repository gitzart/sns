from datetime import datetime, timedelta

from project import db


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

    type = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime)

    left_user = db.relationship('User', foreign_keys=left_user_id)
    right_user = db.relationship('User', foreign_keys=right_user_id)
    action_user = db.relationship('User', foreign_keys=action_user_id)

    def __init__(self, n1, n2, action_user, type, created=None):
        self.left_user = n1
        self.right_user = n2
        self.action_user = action_user
        self.type = type
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<%s %s, %s>' % (
            self.__class__.__name__,
            self.left_user.name,
            self.right_user.name,
        )

    @classmethod
    def get(cls, n1, n2):
        """Get mutual relationship ``query``."""

        return cls.query.filter(db.or_(
            db.and_(cls.left_user == n1, cls.right_user == n2),
            db.and_(cls.left_user == n2, cls.right_user == n1)
        ))

    @classmethod
    def build(cls, n1, n2, action_user, type):
        created = datetime.utcnow()
        return (cls(n1, n2, action_user, type, created),
                cls(n2, n1, action_user, type, created))

    @classmethod
    def update(cls, n1, n2, action_user, type, lazy=False):
        """
        :param lazy: When True, a new relationship will be built
            if not already existed.
        """
        rv = cls.get(n1, n2).all()

        if rv:
            r1, r2 = rv
            r1.created = r2.created = datetime.utcnow()
            r1.action_user = r2.action_user = action_user
            r1.type = r2.type = type
            return r1, r2

        if lazy:
            return cls.build(n1, n2, action_user, type)

    @classmethod
    def destroy(cls, n1, n2):
        return cls.get(n1, n2).delete(synchronize_session=False)


class Follower(db.Model):
    """Builds following and follower relationships."""

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

    follower = db.relationship('User', foreign_keys=followed_id)
    followed = db.relationship('User', foreign_keys=follower_id)

    def __init__(self, follower, followed, expiration=None, create=None):
        self.follower = follower
        self.followed = followed
        self.expiration = expiration
        self.created = create or datetime.utcnow()

    def __repr__(self):
        return '<%s %s, %s>' % (
            self.__class__.__name__,
            self.follower.name,
            self.followed.name,
        )

    @classmethod
    def get(cls, follower, followed):
        return cls.query.filter(db.and_(
            cls.follower == follower,
            cls.followed == followed,
        ))

    @classmethod
    def build(cls, follower, followed, expiration=None):
        return cls(follower, followed, expiration)

    @classmethod
    def update(cls, follower, followed, expiration=None, lazy=False):
        """
        :param lazy: When True, a new relationship will be built
            if not already existed.
        """
        rv = cls.query.get((follower.id, followed.id))
        if rv:
            rv.expiration = expiration
            return rv
        if lazy:
            return cls.build(follower, followed)

    @classmethod
    def destroy(cls, follower, followed):
        return cls.get(follower, followed).delete(synchronize_session=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime)

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
        backref='followings'
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

    def __init__(self, name):
        self.name = name
        self.created = datetime.utcnow()

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name,
        )

    @property
    def friends(self):
        return self.friendship.filter(Friendship.type == 'friend')

    @staticmethod
    def mutual_friends(n1, n2):
        def criteria(arg):
            return db.and_(
                Friendship.left_user == arg,
                Friendship.type == 'friend'
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
        return Friendship.get(self, n).filter_by(
            type='friend').count() > 0

    def is_mutual_firend(self, n1, n2):
        return Friendship.query.filter(db.and_(
            Friendship.left_user == self,
            Friendship.type == 'friend',
            db.or_(
                Friendship.right_user == n1,
                Friendship.right_user == n2
            )
        )).count() == 2

    def is_following(self, n):
        return Follower.get(self, n).count() > 0

    def is_snoozing(self, n):
        return Follower.get(self, n).filter(
            Follower.expiration is not None
        ).count() > 0

    def suggest(self, n1, n2):
        suggestible = Friendship.get(n1, n2).filter(db.or_(
            Friendship.type == 'suggest',
            Friendship.type == 'pending',
            Friendship.type == 'friend',
            Friendship.type == 'block',
        )).count() == 0

        if suggestible and self.is_mutual_firend(n1, n2):
            return Friendship.build(n1, n2, self, 'suggest')
        else:
            return None

    def make_friends(self, n):
        in_relationship = Friendship.get(self, n).filter(db.or_(
            Friendship.type == 'pending',
            Friendship.type == 'friend',
            Friendship.type == 'block',
        )).count() > 0

        if in_relationship:
            return None
        # update if friend suggestion exists, otherwise build
        return Friendship.update(self, n, self, 'pending', lazy=True)

    def accept(self, n):
        # the same user cannot make friend request and accept
        pending = Friendship.get(self, n).filter(db.and_(
            Friendship.type == 'pending',
            Friendship.action_user != self
        )).count() > 0

        if not pending:
            return None

        # follow each other
        Follower.update(self, n, lazy=True)
        Follower.update(n, self, lazy=True)

        return Friendship.update(self, n, self, 'friend')

    def block(self, n):
        blocked = Friendship.get(self, n).filter_by(
            type='block').count() > 0

        if blocked:
            return None
        # build if not in relationship, otherwise update
        return Friendship.update(self, n, self, 'block', lazy=True)

    def unblock(self, n):
        # only the user who blocked can unblock
        blocked = Friendship.get(self, n).filter(
            Friendship.type == 'block',
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
        pending = Friendship.get(self, n).filter_by(
            type='pending').count() > 0

        if not pending:
            return None
        return Friendship.destroy(self, n)

    def follow(self, n):
        if self.is_following(n):
            return None
        return Follower.build(self, n)

    def unfollow(self, n):
        return Follower.destroy(self, n)

    def snooze(self, n, days=30):
        expiration = datetime.utcnow() + timedelta(days=days)
        return Follower.update(self, n, expiration)

    def unsnooze(self, n):
        if self.is_snoozing(n):
            return Follower.update(self, n, expiration=None)
        else:
            return None
