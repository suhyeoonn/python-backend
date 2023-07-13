import bcrypt
from datetime   import datetime, timedelta
import jwt

class UserService:
    def __init__(self, user_dao, config):
        self.user_dao = user_dao
        self.config = config
    
    def create_new_user(self, new_user):
        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt())
        new_user_id = self.user_dao.insert_user(new_user)
        new_user = self.user_dao.get_user(new_user_id)
        return new_user
    
    def login(self, credential):
        row = self.user_dao.get_user_id_and_password(credential['email'])

        password = credential['password'] 

        return row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8'))
    
    def get_user_id_and_password(self, email):
       return self.user_dao.get_user_id_and_password(email)
    
    def create_token(self, user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds = 60 * 60 * 24)
        }

        return jwt.encode(payload, self.config.JWT_SECRET_KEY, 'HS256')
    
    def follow(self, paylod):
        self.user_dao.insert_follow(paylod)

    def unfollow(self, payload):
        self.user_dao.delete_follow(payload)

    def save_profile_picture(self, picture, filename, user_id):
        profile_pic_path_and_name = os.path.join(self.config['UPLOAD_DIRECTORY'], filename)
        picture.save(profile_pic_path_and_name)

        return self.user_dao.save_profile_picture(profile_pic_path_and_name, user_id)

