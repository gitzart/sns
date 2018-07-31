# flake8: noqa

"""Initialize db

Revision ID: 5fdb9ce036de
Revises:
Create Date: 2018-07-29 18:15:55.602101

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5fdb9ce036de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('blacklist_tokens',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('exp', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('gender', sa.Enum('female', 'male', 'others', name='gender'), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('marital_status', sa.Enum('civil union', 'complicated', 'divorced', 'domestic partnership', 'married', 'open relationship', 'separated', 'single', 'taken', 'widowed', name='marital_status'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('is_snoozed', sa.Boolean(), server_default='f', nullable=True),
    sa.Column('expiration', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    op.create_table('friendships',
    sa.Column('left_user_id', sa.Integer(), nullable=False),
    sa.Column('right_user_id', sa.Integer(), nullable=False),
    sa.Column('action_user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', statement_timestamp())"), nullable=True),
    sa.Column('state', sa.Enum('accepted', 'blocked', 'pending', 'suggested', name='friendship_state'), nullable=False),
    sa.CheckConstraint('left_user_id <> right_user_id'),
    sa.PrimaryKeyConstraint('left_user_id', 'right_user_id')
    )
    op.create_table('photo_albums',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('cover_photo_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('caption', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('album_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_album_contributions',
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.Column('contributor_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('album_id', 'contributor_id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('photo_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_reactions',
    sa.Column('actor_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('reaction', sa.Enum('angry', 'laugh', 'like', 'love', 'sad', 'wow', name='reaction'), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('actor_id', 'post_id')
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('root_comment_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment_reactions',
    sa.Column('actor_id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.Column('reaction', sa.Enum('angry', 'laugh', 'like', 'love', 'sad', 'wow', name='reaction'), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('actor_id', 'comment_id')
    )
    # Alter tables' constraints
    op.create_foreign_key(None, 'followers', 'users', ['followed_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'followers', 'users', ['follower_id'], ['id'], ondelete='CASCADE')

    op.create_foreign_key(None, 'friendships', 'users', ['action_user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'friendships', 'users', ['left_user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'friendships', 'users', ['right_user_id'], ['id'], ondelete='CASCADE')

    op.create_foreign_key('photo_albums_cover_photo_id_fkey', 'photo_albums', 'photos', ['cover_photo_id'], ['id'])
    op.create_foreign_key(None, 'photo_albums', 'users', ['owner_id'], ['id'])

    op.create_foreign_key(None, 'photos', 'photo_albums', ['album_id'], ['id'])
    op.create_foreign_key(None, 'photos', 'users', ['owner_id'], ['id'])

    op.create_foreign_key(None, 'photo_album_contributions', 'photo_albums', ['album_id'], ['id'])
    op.create_foreign_key(None, 'photo_album_contributions', 'users', ['contributor_id'], ['id'])

    op.create_foreign_key(None, 'posts', 'users', ['author_id'], ['id'])
    op.create_foreign_key(None, 'posts', 'photos', ['photo_id'], ['id'])

    op.create_foreign_key(None, 'post_reactions', 'users', ['actor_id'], ['id'])
    op.create_foreign_key(None, 'post_reactions', 'posts', ['post_id'], ['id'])

    op.create_foreign_key(None, 'comments', 'users', ['author_id'], ['id'])
    op.create_foreign_key(None, 'comments', 'posts', ['post_id'], ['id'])
    op.create_foreign_key(None, 'comments', 'comments', ['root_comment_id'], ['id'])

    op.create_foreign_key(None, 'comment_reactions', 'users', ['actor_id'], ['id'])
    op.create_foreign_key(None, 'comment_reactions', 'comments', ['comment_id'], ['id'])


def downgrade():
    tables = [
        'users', 'posts', 'post_reactions', 'photos', 'photo_albums',
        'photo_album_contributions', 'friendships', 'followers', 'comments',
        'comment_reactions', 'blacklist_tokens'
    ]
    types = ['friendship_state', 'gender', 'marital_status', 'reaction']
    drop_sqltext = ''

    for table in tables:
        drop_sqltext += f'DROP TABLE {table} CASCADE;'

    for type in types:
        drop_sqltext += f'DROP TYPE {type} CASCADE;'

    op.execute(drop_sqltext)
