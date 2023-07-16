import config

from flask import Flask, jsonify, request, current_app, Response, g

from sqlalchemy import create_engine, text
from flask_cors import CORS

from model import UserDao, TweetDao
from service import UserService, TweetService
from view import create_endpoints

import boto3

class Service:
    pass

# current_app: create_app 함수에서 생성한 app 변수를 create_app함수 외부에서도 쓸 수 있게 해준다

def create_app(test_config = None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database = create_engine(app.config['DB_URL'], echo=True)

    # model
    user_dao = UserDao(database)
    tweet_dao = TweetDao(database)

    ## Business Layer
    s3_client = boto3.client(
        "s3",
        aws_access_key_id     = app.config['S3_ACCESS_KEY'],
        aws_secret_access_key = app.config['S3_SECRET_KEY']
    )

    # service
    services = Service
    services.user_service = UserService(user_dao, config, s3_client)
    services.tweet_service = TweetService(tweet_dao, config)
    app.database = database

    # create endpoints
    create_endpoints(app, services)
    
    return app

