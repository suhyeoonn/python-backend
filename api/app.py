from flask import Flask, jsonify, request, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

# default json encoder는 set을 JSON으로 변환할 수 없음
# set을 list로 변환하여 json으로 변환 가능하도록 처리
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)
    

def create_app(test_config = None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    
    database = create_engine(app.config['DB_URL'], echo=True)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    # 회원 가입 API
    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = app.database.execute(text("""
            INSERT INTO users(
                name,
                email,
                profile,
                hashed_password
            ) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
        """), new_user).lastrowid

        row = current_app.database.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {
            'user_id': new_user_id
        }).fetchone()

        created_user = {
            'id':row['id'],
            'name': row['name'],
            'email': row['email'],
            'profile': row['profile']
        } if row else None

        return jsonify(created_user)

    # 트윗 글 올리기 API
    @app.route("/tweet", methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']
        print(user_tweet)

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400
        
        app.database.execute(text("""
            INSERT INTO tweets(
                user_id,
                tweet
            ) VALUES (
                :id,
                :tweet
            )
        """), user_tweet)

        return '', 200

    # 팔로우 API
    @app.route("/follow", methods=['POST'])
    def follow():
        payload = request.json
        user_id = int(payload['id'])
        user_id_to_follow = int(payload['follow'])

        if user_id not in app.users:
            return 'id 사용자가 존재하지 않습니다', 400
        
        if user_id_to_follow not in app.users:
            return 'follow 사용자가 존재하지 않습니다', 400

        user = app.users[user_id]
        # follow 키 없으면 생성
        user.setdefault('follow', set()).add(user_id_to_follow)
        print(user)
        return jsonify(user)

    @app.route("/unfollow", methods=['POST'])
    def unfollow():
        payload = request.json
        user_id = int(payload['id'])
        user_id_to_unfollow = int(payload['unfollow'])

        if user_id not in app.users or user_id_to_unfollow not in app.users:
            return '사용자가 존재하지 않습니다', 400
        
        user = app.users[user_id]
        # 없는 값 삭제 시도 시 무시
        user.setdefault('follow', set()).discard(user_id_to_unfollow)
        return jsonify(user)

    @app.route("/timeline/<int:user_id>", methods=['GET'])
    def timeline(user_id):
        if user_id not in app.users:
            return '사용자가 존재하지 않습니다', 400
        
        follow_list = app.users[user_id].get('follow', set()) # 딕셔너리 get: 키가 없을 경우 디폴트값 대신 가져옴
        follow_list.add(user_id)
        timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]
        
        return jsonify({
            'user_id': user_id,
            'timeline': timeline
        })
    
    return app

