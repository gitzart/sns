class BaseConfig:
    TESTING = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


class StagingConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass
