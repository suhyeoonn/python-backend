import config
from model import UserDao, TweetDao
from sqlalchemy import create_engine, text
import pytest
import bcrypt

database = create_engine(config.test_config['DB_URL'], echo=True)

@pytest.fixture
def user_dao():
    return UserDao(database)

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

def get_follow_list(user_id):
    rows = database.execute(text("""
        SELECT follow_user_id as id
        FROM users_follow_list
        WHERE user_id = :user_id
    """), {
        'user_id': user_id
    }).fetchall()

    return [int(row['id']) for row in rows]

def test_insert_user(user_dao):
    new_user = {
        'id': 11,
        'name': 'eee',
        'email': 'test@gmail.com',
        'profile': 'test profile',
        'password': 'test1234'
    }

    new_user_id = user_dao.insert_user(new_user)
    user = user_dao.get_user(new_user_id)

    assert user == {
        'id': new_user_id,
        'name': new_user['name'],
        'email': new_user['email'],
        'profile': new_user['profile']
    }

def test_get_user_id_and_password(user_dao):
    email = 'aaa@gmail.com'
    user = user_dao.get_user_id_and_password(email)
    
    # 사용자 아이디 일치하는지 확인
    assert user['id'] == 1

    assert bcrypt.checkpw('test password'.encode('UTF-8'), user['hashed_password'].encode('UTF-8'))

def test_insert_follow(user_dao):
    user_dao.insert_follow({
        "id": 11,
        "follow": 1
    })

    follow_list = get_follow_list(11)

    assert follow_list == [1]
    
def test_insert_unfollow(user_dao):
    user_dao.delete_follow({"id" : 11, "unfollow" : 1})
    follow_list = get_follow_list(11)

    assert follow_list == []

def test_save_and_get_profile_picture(user_dao):
    user_id = 1
    # 저장한게 없으니 None이 나와야 한다
    user_profile_picture = user_dao.get_profile_picture(user_id)
    assert user_profile_picture is None

    # 파일 저장
    expected_profile_picture = "s3://python-backend/KakaoTalk_Photo_2023-05-24-06-31-12_002.jpeg"
    user_dao.save_profile_picture(expected_profile_picture, user_id)

    # 저장된 값과 기대값 비교
    actual_profile_picture = user_dao.get_profile_picture(user_id)
    assert expected_profile_picture == actual_profile_picture
