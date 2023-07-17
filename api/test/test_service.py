import config
from model import UserDao, TweetDao
from service import UserService
from sqlalchemy import create_engine, text
import pytest
import bcrypt
from unittest   import mock

database = create_engine(config.test_config['DB_URL'], echo=True)

@pytest.fixture
def user_service():
    mock_s3_client = mock.Mock()
    return UserService(UserDao(database), config.test_config, mock_s3_client)

def setup_function():
    #create test user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )

    new_user = {
        'id': 13,
        'name': 'aaa',
        'email': 'aaa@gmail.com',
        'profile': 'aa profile',
        'password': hashed_password
    }
    database.execute(text("""
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
        """), new_user)
    
def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE tweets"))
    database.execute(text("TRUNCATE users_follow_list"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))

def get_user(user_id):
    row = database.execute(text("""
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

    return {
        'id': row['id'],
        'name': row['name'],
        'email': row['email'],
        'profile': row['profile'],
    } if row else None

def test_create_new_user(user_service):
    new_user = {
        'name': 'bbb',
        'email': 'bbb@gmail.com',
        'profile': 'aa profile',
        'password': 'hashed_password'
    }
    
    created_user = user_service.create_new_user(new_user)
    
    # created_user = get_user(new_user['id'])
    assert created_user == {
        'id': created_user['id'],
        'name': new_user['name'],
        'profile': new_user['profile'],
        'email': new_user['email'],
    }

def test_save_and_get_profile_picture(user_service):
    user_id = 1
    user_profile_picture = user_service.get_profile_picture(user_id)
    assert user_profile_picture is None

    test_pic = mock.Mock()
    filename = "test.png"
    user_service.save_profile_picture(test_pic, filename, user_id)

    acturl_profile_picture = user_service.get_profile_picture(user_id)
    assert acturl_profile_picture == "https://s3.ap-northeast-2.amazonaws.com/test/test.png"