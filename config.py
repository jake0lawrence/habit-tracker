import os
import datetime


class BaseConfig:
    DEBUG = False
    TESTING = False
    PWA_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)

class DevConfig(BaseConfig):
    DEBUG = True
    PWA_ENABLED = False

class ProdConfig(BaseConfig):
    PWA_ENABLED = True
