import bcrypt
from datetime   import datetime, timedelta
import jwt
import os
import boto3

class UserService:
    def __init__(self, user_dao, config, s3_client):
        self.user_dao = user_dao
        self.config = config
        self.s3       = s3_client
    
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
        self.s3.upload_fileobj(
            picture,
            self.config.S3_BUCKET,
            filename
        )

        image_url = f"{self.config.S3_BUCKET_URL}{filename}"

        return self.user_dao.save_profile_picture(image_url, user_id)
    
    def get_profile_picture(self, user_id):
        return self.user_dao.get_profile_picture(user_id)

