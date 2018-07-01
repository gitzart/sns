import os


def test_development_config(app):
    app.config.from_object('project.config.DevelopmentConfig')
    assert not app.testing
    assert app.debug
    assert app.config['SECRET_KEY'] == 'my_precious'
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.getenv('DATABASE_URL')
    assert not app.config['SQLALCHEMY_ECHO']
    assert app.config['DEBUG_TB_ENABLED']
    assert app.config['BCRYPT_LOG_ROUNDS'] == 4


def test_testing_config(app):
    app.config.from_object('project.config.TestingConfig')
    assert app.testing
    assert app.debug
    assert app.config['SECRET_KEY'] == 'my_precious'
    assert (app.config['SQLALCHEMY_DATABASE_URI'] ==
            os.getenv('DATABASE_TEST_URL'))
    assert app.config['SQLALCHEMY_ECHO'] == 'debug'
    assert not app.config['DEBUG_TB_ENABLED']
    assert app.config['BCRYPT_LOG_ROUNDS'] == 4


def test_production_config(app):
    app.config.from_object('project.config.ProductionConfig')
    assert not app.testing
    assert not app.debug
    assert not app.config['SQLALCHEMY_ECHO']
    assert not app.config['DEBUG_TB_ENABLED']
    assert app.config['BCRYPT_LOG_ROUNDS'] == 12
