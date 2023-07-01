from datetime   import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, current_app, Response, g
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import bcrypt
import jwt
from flask_cors import CORS

# default json encoder는 set을 JSON으로 변환할 수 없음
# set을 list로 변환하여 json으로 변환 가능하도록 처리
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)
    

# current_app: create_app 함수에서 생성한 app 변수를 create_app함수 외부에서도 쓸 수 있게 해준다
def insert_user(new_user):
    new_id = current_app.database.execute(text("""
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
    return new_id

def get_user(user_id):
    user = current_app.database.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {
            'user_id': user_id
        }).fetchone()
    
    return  {
            'id':user['id'],
            'name': user['name'],
            'email': user['email'],
            'profile': user['profile']
        } if user else None

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

def insert_follow(user_follow):
    return current_app.database.execute(text("""
            INSERT INTO users_follow_list(
                user_id,
                follow_user_id
            ) VALUES (
                :id,
                :follow
            )
        """), user_follow).rowcount    

def delete_follow(user_unfollow):
    return current_app.database.execute(text("""
            DELETE FROM users_follow_list
            WHERE user_id = :id AND follow_user_id = :unfollow
        """), user_unfollow).rowcount 

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

def check_user(email):
    return current_app.database.execute(text("""
            SELECT
                id,
                hashed_password
            FROM users
            WHERE email = :email
        """), {'email': email}).fetchone()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
            except jwt.InvalidTokenError:
                payload = None

            if payload is None: return Response(status=401)

            user_id = payload['user_id']
            g.user_id = user_id
            g.user = get_user(user_id) if user_id else None
        else:
            return Response(status = 401)
        
        return f(*args, **kwargs)
    return decorated_function

def create_app(test_config = None):
    app = Flask(__name__)

    CORS(app)

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
        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt())
        new_user_id = insert_user(new_user)

        created_user = get_user(new_user_id)

        return jsonify(created_user)
    
    # 로그인
    @app.route("/login", methods=['POST'])
    def login():
        credential = request.json
        row = check_user(credential['email'])

        password = credential['password'] 

        if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
            user_id = row['id']
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds = 60 * 60 * 24)
            }

            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')

            return jsonify({
                'access_token' : token
            })
        else :
            return '', 401
        


    # 트윗 글 올리기 API
    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet['id'] = g.user_id
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400
        
        insert_tweet(user_tweet)

        return '', 200

    # 팔로우 API
    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        insert_follow(payload)

        return '', 200

    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        delete_follow(payload)
        
        return '', 200
    
    @app.route("/timeline", methods=['GET'])
    @login_required
    def timeline():
        user_id = g.user_id

        return jsonify({
            'user_id': user_id,
            'timeline': get_timeline(user_id)
        })
    
    return app

