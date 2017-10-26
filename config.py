# -*- coding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    #SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    BABEL_DEFAULT_LOCALE = 'zh'
    # 公司邮箱域名后缀，限制只能公司域名才能注册
    COMPANY_MAIL_SUFFIX='qq.com'
    # send mail
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '2399447849@qq.com' #os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = '' #os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = u'[花花]'
    FLASKY_MAIL_SENDER = '2399447849@qq.com'
    FLASKY_ADMIN = '2399447849@qq.com' # os.environ.get('FANXIANG_ADMIN')    

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    db_host = '127.0.0.1'
    db_user = 'flask'
    db_pass = 'flask'
    db_name = 'flask4'
    SQLALCHEMY_DATABASE_URI = 'mysql://' + db_user + ':' + db_pass + '@' + db_host + '/' + db_name
    SQLALCHEMY_ECHO=False #用于显式地禁用或启用查询记录

    ##SQLALCHEMY_DATABASE_URI = 'mysql://flask1:flask1@127.0.0.1/flask1'
    SQLALCHEMY_TRACK_MODIFICATIONS=True

    #google 验证码
    RECAPTCHA_PUBLIC_KEY = '6LesDBYUAAAAADcO0A-3X11Jm41gPKM2BSk-dtWC'
    RECAPTCHA_PRIVATE_KEY = '6LesDBYUAAAAAIdPUNGhUYFMMZ_oDF3Mo8enwrXH'


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask-test'
    WTF_CSRF_ENABLED = False


class Production(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask-pro'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': Production,
    'default': DevelopmentConfig
}
