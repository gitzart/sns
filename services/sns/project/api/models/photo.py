from datetime import datetime

from project import db


class PhotoAlbumContribution(db.Model):
    """Represents the association of the user and
    the photo album the user contributes to.
    """

    __tablename__ = 'photo_album_contributions'

    album_id = db.Column(
        db.Integer,
        db.ForeignKey('photo_albums.id'),
        primary_key=True
    )

    contributor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )

    created = db.Column(db.DateTime)

    album = db.relationship(
        'PhotoAlbum',
        back_populates='contributors'
    )

    contributor = db.relationship(
        'User',
        back_populates='associated_albums'
    )

    def __init__(self, album, contributor, created=None):
        self.album = album
        self.contributor = contributor
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<%s %s, %s>' % (
            self.__class__.__name__,
            self.album.title,
            self.contributor.first_name
        )


class PhotoAlbum(db.Model):
    __tablename__ = 'photo_albums'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    cover_photo_id = db.Column(
        db.Integer,
        db.ForeignKey('photos.id', name='photo_albums_cover_photo_id_fkey')
    )

    owner = db.relationship(
        'User',
        lazy='joined',
        back_populates='photo_albums'
    )

    cover_photo = db.relationship(
        'Photo',
        foreign_keys=cover_photo_id,
        lazy='joined'
    )

    photos = db.relationship(
        'Photo',
        foreign_keys='Photo.album_id',
        lazy='dynamic',
        back_populates='album'
    )

    contributors = db.relationship(
        'PhotoAlbumContribution',
        lazy='dynamic',
        back_populates='album'
    )

    def __init__(self, title, created=None, updated=None):
        self.title = title
        self.created = created
        self.updated = updated

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.title,
        )


class Photo(db.Model):
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    caption = db.Column(db.String)
    created = db.Column(db.DateTime)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('photo_albums.id'))

    owner = db.relationship(
        'User',
        lazy='joined',
        back_populates='photos'
    )

    album = db.relationship(
        'PhotoAlbum',
        foreign_keys=album_id,
        lazy='joined',
        back_populates='photos'
    )

    # photo post
    post = db.relationship(
        'Post',
        lazy='joined',
        cascade='all, delete-orphan',
        uselist=False,
        back_populates='photo'
    )

    def __init__(self, caption=None, created=None):
        self.caption = caption
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.caption or self.id,
        )

    def is_album_cover(self):
        return PhotoAlbum.query.filter_by(cover_photo_id=self.id). \
            first() is not None
