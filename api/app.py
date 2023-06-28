from flask import Flask, jsonify, request
from flask.json import JSONEncoder

app = Flask(__name__)

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

app.users = {
    1: {'name': 'elly', 'email': 'elly@abc.com', 'password': '1234', 'id': 1}
}
app.id_count = 2
app.tweets = []

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)
app.json_encoder = CustomJSONEncoder

# 회원 가입 API
@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json
    new_user["id"] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    print(app.users)
    return jsonify(new_user)

# 트윗 글 올리기 API
@app.route("/tweet", methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400
    
    if len(tweet) > 300:
        return '300자를 초과했습니다', 400
    
    app.tweets.append({
        'user_id': user_id,
        'tweet': tweet
    })

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
