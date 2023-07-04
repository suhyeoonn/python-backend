import config

from flask import Flask, jsonify, request, current_app, Response, g

from sqlalchemy import create_engine, text
from flask_cors import CORS

from model import UserDao
from service import UserService
from view import create_endpoints

class Service:
    pass


    

# current_app: create_app 함수에서 생성한 app 변수를 create_app함수 외부에서도 쓸 수 있게 해준다




def insert_tweet(user_tweet):
    return current_app.database.execute(text("""
            INSERT INTO tweets(
                user_id,
                tweet
            ) VALUES (
                :id,
                :tweet
            )
        """), user_tweet).rowcount


def get_timeline(user_id):
    rows = current_app.database.execute(text("""
            select t.user_id, t.tweet
            from tweets t
            left join users_follow_list ufl on ufl.user_id = :user_id
            where t.user_id = :user_id or t.user_id = ufl.follow_user_id
        """), {
            'user_id': user_id
        }).fetchall()

    return [{
        'user_id': row['user_id'],
        'tweet': row['tweet']
    } for row in rows]


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

    # service
    services = Service
    services.user_service = UserService(user_dao, config)
    app.database = database

    # create endpoints
    create_endpoints(app, services)
    
    
    
        


    # # 트윗 글 올리기 API
    # @app.route("/tweet", methods=['POST'])
    # @login_required
    # def tweet():
    #     user_tweet = request.json
    #     user_tweet['id'] = g.user_id
    #     tweet = user_tweet['tweet']

    #     if len(tweet) > 300:
    #         return '300자를 초과했습니다', 400
        
    #     insert_tweet(user_tweet)

    #     return '', 200

    
    # @app.route("/timeline", methods=['GET'])
    # @login_required
    # def timeline():
    #     user_id = g.user_id

    #     return jsonify({
    #         'user_id': user_id,
    #         'timeline': get_timeline(user_id)
    #     })
    
    return app

