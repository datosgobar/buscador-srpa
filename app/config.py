import os


class Config(object):
    TESTING = False
    DEBUG = True
    CSRF_ENABLED = False
    USER_APP_NAME = "PreguntasJGM"
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ENABLE_USERNAME = False
    USER_ENABLE_CHANGE_USERNAME = False
    USER_ENABLE_REGISTRATION = False
    BABEL_DEFAULT_LOCALE = 'es'
    WERKZEUG_DEBUG_PIN = '123456'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    SECRET_KEY = 'THIS IS AN INSECURE SECRET'

    MAIL_USERNAME = 'JGM\datos'
    MAIL_DEFAULT_SENDER = 'datos@modernizacion.gob.ar'
    MAIL_SERVER = 'owa.jgm.gob.ar'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_PASSWORD = os.environ.get('SMTP_PASS', '')
