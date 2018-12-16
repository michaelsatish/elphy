import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('No secret key set for Flask application')


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGO_URI')
    }


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGO_URI')
    }


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
