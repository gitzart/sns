import pytest

from flask.cli import FlaskGroup

from project import create_app, db


cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    '''Run the tests without code coverage'''
    pytest.main([])


if __name__ == '__main__':
    cli()
