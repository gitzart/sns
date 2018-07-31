import sys

import click
import coverage
import pytest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import *  # noqa


cov = coverage.Coverage(
    branch=True,
    include='project/api/*',
)
cov.start()

cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def load_db():
    with open('data.sql') as file:
        db.engine.execute(file.read())


@cli.command()
@click.option('-c', '--coverage', is_flag=True)
def test(coverage):
    rv = pytest.main([])
    if rv == 0:
        if coverage:
            cov.stop()
            cov.save()
            print('Coverage Summary:')
            cov.report(show_missing=True, skip_covered=True)
            cov.html_report()
            cov.erase()
        sys.exit(0)
    sys.exit(1)


if __name__ == '__main__':
    cli()
