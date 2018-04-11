from datetime import datetime

from project import db


GenderEnum = db.Enum('male', 'female', 'others', name='gender')
PhotoTypeEnum = db.Enum('standard', 'comment', name='photo_type')
RelationshipStatusEnum = db.Enum(
    'single', 'taken', 'married', 'divorced', 'separated', 'others',
    name='relationship_status'
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    gender = 'male'
    intro = db.Column(db.Text)
    current_city = db.Column(db.String)
    relationship_status = 'single'
    birth_date = db.Column(db.DateTime, default=datetime.utcnow())
    created_on = db.Column(db.DateTime, default=datetime.utcnow())
    posts = db.relationship('Post', back_populates='author',
                            cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author',
                               cascade='all, delete-orphan')
    photos = db.relationship('Photo', back_populates='owner',
                             cascade='all, delete-orphan')


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    expressions = 'feeling'
    exposed_to = 'shared_with'
    edit_history = 'versions'
    shares = ''
    state = 'hidden'
    created_on = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post',
                               cascade='all, delete-orphan',
                               order_by='Comment.create_on.desc()')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    expressions = 'feeling'
    exposed_to = 'shared_with'
    edit_history = 'versions'
    replies = ''
    create_on = db.Column(db.DateTime, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='comments')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Post', back_populates='comments')


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    expressions = 'feeling'
    exposed_to = 'shared_with'
    type = 'profile'
    created_on = db.Column(db.DateTime, default=datetime.utcnow())
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = db.relationship('User', back_populates='photos')
