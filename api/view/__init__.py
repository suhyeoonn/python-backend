from flask import jsonify, request
from flask.json import JSONEncoder
from functools import wraps
import jwt
from flask import Flask, jsonify, request, current_app, Response, g, send_file
from werkzeug.utils import secure_filename

# default json encoder는 set을 JSON으로 변환할 수 없음
# set을 list로 변환하여 json으로 변환 가능하도록 처리
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)
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
        else:
            return Response(status = 401)
        
        return f(*args, **kwargs)
    return decorated_function
    
def create_endpoints(app, services):
    app.json_encoder = CustomJSONEncoder

    user_service = services.user_service
    tweet_service = services.tweet_service

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    # 회원 가입 API
    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        created_user = user_service.create_new_user(new_user)

        return jsonify(created_user)
    
    # 로그인
    @app.route("/login", methods=['POST'])
    def login():
        credential = request.json
        authorized = user_service.login(credential)
        if authorized:
            user = user_service.get_user_id_and_password(credential['email'])
            token = user_service.create_token(user["id"])

            return jsonify({
                'access_token' : token
            })
        else :
            return '', 401
        
    # 팔로우 API
    @app.route("/follow", methods=['POST'])
    @login_required
    def follow():
        payload = request.json
        user_service.follow(payload)

        return '', 200
    
    @app.route("/unfollow", methods=['POST'])
    @login_required
    def unfollow():
        payload = request.json
        user_service.unfollow(payload)
        
        return '', 200

    @app.route("/timeline", methods=['GET'])
    @login_required
    def timeline():
        user_id = g.user_id

        return jsonify({
            'user_id': user_id,
            'timeline': tweet_service.get_timeline(user_id)
        })
    
    # 트윗 글 올리기 API
    @app.route("/tweet", methods=['POST'])
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet['id'] = g.user_id
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400
        
        tweet_service.insert_tweet(user_tweet)

        return '', 200
    
    # 파일 업로드
    @app.route('/profile-picture', methods=['POST'])
    @login_required
    def upload_profile_picture():
        user_id = g.user_id

        if 'profile_pic' not in request.files:
            return 'File is missing', 404
        
        profile_pic = request.files['profile_pic']

        if profile_pic.filename == '':
            return 'File is missing', 404
        
        filename = secure_filename(profile_pic.filename)
        user_service.save_profile_picture(profile_pic, filename, user_id)

        return '', 200
    
    # 파일 보기
    @app.route('/profile-picture/<int:user_id>', methods=['GET'])
    def get_profile_picture(user_id):
        profile_picture = user_service.get_profile_picture(user_id)

        if profile_picture:
            return jsonify({'img_url': profile_picture})
        else:
            return '', 404