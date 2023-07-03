from flask import jsonify, request
from flask.json import JSONEncoder

# default json encoder는 set을 JSON으로 변환할 수 없음
# set을 list로 변환하여 json으로 변환 가능하도록 처리
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return JSONEncoder.default(self, obj)
    
def create_endpoints(app, services):
    app.json_encoder = CustomJSONEncoder

    user_service = services.user_service

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    # 회원 가입 API
    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        created_user = user_service.create_new_user(new_user)

        return jsonify(created_user)