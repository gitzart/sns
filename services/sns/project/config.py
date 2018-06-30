import os


class BaseConfig:
    TESTING = False
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DENUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 4


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL')
    SQLALCHEMY_ECHO = 'debug'


class StagingConfig(BaseConfig):
    BCRYPT_LOG_ROUNDS = 12


class ProductionConfig(BaseConfig):
    BCRYPT_LOG_ROUNDS = 12
