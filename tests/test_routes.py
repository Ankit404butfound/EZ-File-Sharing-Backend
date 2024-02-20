import unittest
import json
from main import app, db, User, File

def setup_module(module):
    app.testing = True
    global test_app
    test_app = app.test_client()
    

def test_index():
    response = test_app.get('/')
    assert response.status_code == 200
    assert response.data.decode() == "Hello, World!"


def test_signup():
    with test_app as ta:
        with ta.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'CLIENT'
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "password",
            "user_type": "CLIENT"
        }
        response = test_app.post('/user/signup', data=data)
        print(response)
    assert response.status_code == 201 or response.status_code == 409


def test_signup_missing_fields():
    data = {
        "username": "testuser2",
        "password": "password",
        "user_type": "CLIENT"
    }
    response = test_app.post('/user/signup', data=data)
    print(response)
    assert response.status_code == 400
    json_data = json.loads(response.data)
    assert not json_data['status']
    assert json_data['message'] == "Missing required fields"


def test_signup_existing_user():
    data = {
        "username": "testuser",
        "email": "test2@example.com",
        "password": "password",
        "user_type": "CLIENT"
    }
    response = test_app.post('/user/signup', data=data)
    assert response.status_code == 409
    json_data = json.loads(response.data)
    assert not json_data['status']
    assert json_data['message'] == "User with this username or email already exists"


def test_login():
    data = {
        "username": "testuser",
        "password": "password"
    }
    response = test_app.post('/user/login', data=data)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['status']
    assert json_data['message'] == "User logged in successfully"
    assert json_data['user']['username'] == "testuser"


def test_login_invalid_credentials():
    data = {
        "username": "nonexistentuser",
        "password": "invalidpassword"
    }
    response = test_app.post('/user/login', data=data)
    assert response.status_code == 401 or response.status_code == 404


def test_logout():
    with test_app as ta:
        with ta.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'CLIENT'
    response = test_app.get('/user/logout')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['status']
    assert json_data['message'] == "User logged out successfully"


def test_upload_file():
    with test_app as ta:
        with ta.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'OPS'
        data = {'file': (open('tests/test_file.xlsx', 'rb'), 'test_file.xlsx')}
        response = ta.post('/file/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 201


def test_list_files():
    with test_app as ta:
        with ta.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'CLIENT'
    response = test_app.get('/file/list')
    assert response.status_code == 200


def test_download_file():
    with test_app as ta:
        with ta.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'CLIENT'
    response = test_app.get('/file/download?file_hash=test')
    print(response.text)
    assert response.status_code == 200 or response.status_code == 404



# setUp()
# unittest.main()
