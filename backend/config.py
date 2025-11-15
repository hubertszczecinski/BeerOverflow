import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-central-1')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'bank.db')

config = {
    'default': Config
}
