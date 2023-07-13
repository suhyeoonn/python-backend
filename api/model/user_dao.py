from sqlalchemy import create_engine, text

class UserDao:
    def __init__(self, database):
        self.db = database

    def insert_user(self, user):
        return self.db.execute(text("""
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
        """), user).lastrowid
    
    def get_user(self, user_id):
        user = self.db.execute(text("""
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
    
    def get_user_id_and_password(self, email):
        return self.db.execute(text("""
                SELECT
                    id,
                    hashed_password
                FROM users
                WHERE email = :email
            """), {'email': email}).fetchone()
    
    def insert_follow(self, user_follow):
        return self.db.execute(text("""
            INSERT INTO users_follow_list(
                user_id,
                follow_user_id
            ) VALUES (
                :id,
                :follow
            )
        """), user_follow).rowcount    

    def delete_follow(self, user_unfollow):
        return self.db.execute(text("""
            DELETE FROM users_follow_list
            WHERE user_id = :id AND follow_user_id = :unfollow
        """), user_unfollow).rowcount 
    
    def save_profile_picture(self, profile_pic_path, user_id):
        return self.db.execute(text("""
            UPDATE users
            SET profile_picture = :profile_pic_path
            WHERE id = :user_id
        """), {
            'user_id': user_id,
            'profile_pic_path': profile_pic_path
        }).rowcount