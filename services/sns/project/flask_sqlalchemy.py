# SQLAlchemy extension (Modification of Flask_SQLAlchemy)

from threading import Lock

from flask import _app_ctx_stack, current_app
from sqlalchemy import create_engine, orm
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base


def get_state(app):
    '''Get the state for the application.'''
    assert 'sqlalchemy' in app.extensions, \
        'Make sure you call init_app() first.'
    return app.extensions['sqlalchemy']


class FSASession(orm.session.Session):
    '''Unlike original Flask_SQLAlchemy `SignallingSession`,
    this class does not extend `orm.session.Session`,
    but to avoid application context exception.
    '''

    def __init__(self, db, options):
        orm.session.Session.__init__(
            self, bind=db.engine, **options
        )


class _Connector:
    '''Helper class to hold database `engine` and `uri`.'''

    def __init__(self, engine=None, uri=None):
        self.engine = engine
        self.uri = uri


class SQLAlchemy:
    '''Flask extension for SQLAlchemy.'''

    def __init__(self, app=None, session_options=None):
        self.session = self.create_scoped_session(session_options)
        self.Base = declarative_base()
        self.Base.query = self.session.query_property()
        self._engine_lock = Lock()
        self.app = app

        if app is not None:
            self.init_app(app)

    def __repr__(self):
        return '<%s engine=%r>' % (
            self.__class__.__name__,
            self.engine.url if self.app or current_app else None
        )

    def init_app(self, app):
        app.config.setdefault('DATABASE_URL', 'sqlite:///:memory:')
        app.extensions['sqlalchemy'] = {'db': self, 'connector': None}

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.session.remove()

    def create_scoped_session(self, options=None):
        '''If `scopefunc` is not set on the `options` dict,
        Flask's app context stack identity is used to ensure
        the uniqueness of the `sqlalchemy.Session` object.

        :param options: dict of keyword arguments passed to
            session class in `create_session`
        '''

        if options is None:
            options = {}

        scopefunc = options.pop(
            'scopefunc', _app_ctx_stack.__ident_func__
        )
        return orm.scoped_session(
            self.create_session(options), scopefunc=scopefunc
        )

    def create_session(self, options):
        '''Create the session factory.
        By default, `autocommit` and `autoflush` are set to False
        if not set on `options` dict.

        :param options: dict of keyword arguments passed to
            session class
        '''
        options.setdefault('autocommit', False)
        options.setdefault('autoflush', False)
        return orm.sessionmaker(class_=FSASession, db=self, **options)

    @property
    def engine(self):
        return self.get_engine()

    def get_engine(self, app=None):
        '''Return a specific engine.'''

        app = self.get_app(app)
        state = get_state(app)

        # REVIEW: Don't know the use of `threading.Lock`
        # in Flask_SQLAlchemy get_engine() method
        with self._engine_lock:
            connector = state['connector']
            uri = app.config['DATABASE_URL']

            if connector and connector.uri == uri:
                return connector.engine

            info = make_url(uri)
            options = {'convert_unicode': True}
            connector = _Connector(
                create_engine(info, **options), uri
            )
            state['connector'] = connector
            return connector.engine

    def get_app(self, reference_app=None):
        '''Helper method that implements the logic to look up an
        application.'''

        if reference_app:
            return reference_app

        if current_app:
            return current_app._get_current_object()

        if self.app is not None:
            return self.app

        raise RuntimeError(
            'No application found. Either work inside a view function'
            ' or push an application context. See'
            ' http://flask-sqlalchemy.pocoo.org/contexts/.'
        )

    def _execute_for_all_tables(self, app, operation):
        app = self.get_app(app)
        op = getattr(self.Base.metadata, operation)
        op(bind=self.get_engine(app))

    def create_all(self, app=None):
        '''Create all tables.'''
        self._execute_for_all_tables(app, 'create_all')

    def drop_all(self, app=None):
        '''Drop all tables.'''
        self._execute_for_all_tables(app, 'drop_all')
