import bcrypt

class UserService:
    def __init__(self, user_dao, config):
        self.user_dao = user_dao
        self.config = config
    
    def create_new_user(self, new_user):
        new_user['password'] = bcrypt.hashpw(new_user['password'].encode('UTF-8'), bcrypt.gensalt())
        new_user_id = self.user_dao.insert_user(new_user)
        new_user = self.user_dao.get_user(new_user_id)
        return new_user