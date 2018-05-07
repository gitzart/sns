import click
import coverage
import pytest

from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import *


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
@click.option('-c', '--coverage', is_flag=True)
def test(coverage):
    rv = pytest.main([])
    if coverage and rv == 0:
        cov.stop()
        cov.save()
        print('Coverage Summary:')
        cov.report(show_missing=True, skip_covered=True)
        cov.html_report()
        cov.erase()
        return 0
    return rv


if __name__ == '__main__':
    cli()
