class BaseConfig:
    DEBUG = False
    TESTING = False
    PWA_ENABLED = False

class DevConfig(BaseConfig):
    DEBUG = True
    PWA_ENABLED = False

class ProdConfig(BaseConfig):
    PWA_ENABLED = True
