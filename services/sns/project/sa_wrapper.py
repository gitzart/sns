# SQLAlchemy extension

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base


class SQLAlchemy:
    '''A small SQLAlchemy wrapper class.'''

    def __init__(self, app=None):
        self.Base = declarative_base()

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        '''Initialize an application for the use
        with this database setup.
        '''
        self.engine = create_engine(
            app.config['DATABASE_URL'],
            convert_unicode=True,
        )
        session_factory = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        self.session = orm.scoped_session(session_factory)
        self.Base.query = self.session.query_property()

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            self.session.remove()

    def _execute_for_all_tables(self, operation):
        op = getattr(self.Base.metadata, operation)
        op(bind=self.engine)

    def create_all(self):
        self._execute_for_all_tables('create_all')

    def drop_all(self):
        self._execute_for_all_tables('drop_all')