from datetime import datetime

from project import db
from project.utils import to_sa_enum
from .enums import Reaction


SAReaction = to_sa_enum(Reaction)


class CommentReaction(db.Model):
    """Users' reactions to the comment."""

    __tablename__ = 'comment_reactions'

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id'),
        primary_key=True
    )

    reaction = db.Column(SAReaction, nullable=False)
    created = db.Column(db.DateTime)

    actor = db.relationship(
        'User',
        lazy='joined',
        back_populates='comment_reactions'
    )

    comment = db.relationship(
        'Comment',
        lazy='joined',
        back_populates='reactions'
    )

    def __init__(self, actor, comment, reaction, created=None):
        self.actor = actor
        self.comment = comment
        self.reaction = reaction
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.reaction,
        )


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    photo_url = db.Column(db.String)  # photo comment?

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # the comment this comment replies to
    root_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    author = db.relationship(
        'User',
        lazy='joined',
        back_populates='comments'
    )

    post = db.relationship(
        'Post',
        lazy='joined',
        back_populates='comments'
    )

    comment_replies = db.relationship(
        'Comment',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    reactions = db.relationship(
        'CommentReaction',
        lazy='dynamic',
        cascade='all, delete-orphan',
        back_populates='comment'
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
