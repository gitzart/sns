from datetime import datetime

from project import db
from project.utils import to_sa_enum
from .enums import Reaction


SAReaction = to_sa_enum(Reaction)


class PostReaction(db.Model):
    """Users' reactions to the post."""

    __tablename__ = 'post_reactions'

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.id'),
        primary_key=True
    )

    reaction = db.Column(SAReaction, nullable=False)
    created = db.Column(db.DateTime)

    actor = db.relationship(
        'User',
        lazy='joined',
        back_populates='post_reactions'
    )

    post = db.relationship(
        'Post',
        lazy='joined',
        back_populates='reactions'
    )

    def __init__(self, actor, post, reaction, created=None):
        self.actor = actor
        self.post = post
        self.reaction = reaction
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.reaction,
        )


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'))

    author = db.relationship(
        'User',
        lazy='joined',
        back_populates='posts'
    )

    # photo post
    photo = db.relationship(
        'Photo',
        lazy='joined',
        back_populates='post'
    )

    comments = db.relationship(
        'Comment',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='post'
    )

    reactions = db.relationship(
        'PostReaction',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='post'
    )

    def __init__(self, content, created=None, updated=None):
        self.content = content
        self.created = created or datetime.utcnow()
        self.updated = updated or datetime.utcnow()

    def __repr__(self):
        return '<%s %d>' % (
            self.__class__.__name__,
            self.id,
        )

    def is_photo_post(self):
        return self.photo is not None
