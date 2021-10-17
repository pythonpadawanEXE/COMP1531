from src import auth,other,config
import re
import pytest
from src.error import InputError
import requests

BASE_URL = config.url

@pytest.fixture(autouse=True)
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}


def register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last
    })
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data

def login_valid_user(email = 'validemail@gmail.com',password = '123abc!@#'):
    response = requests.post(f"{BASE_URL}/auth/login/v2",json={
        'email' : email,
        'password' : password
    })
    assert response.status_code == 200
    response_data = response.json()
    print(response_data)
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data

def login_invalid_user(email = 'validemail@gmail.com',password = '123abc!@#'):
response = requests.post(f"{BASE_URL}/auth/login/v2",json={
    'email' : email,
    'password' : password
})
assert response.status_code == 400


def logout__valid_user(token):
    response = requests.post(f"{BASE_URL}/auth/logout/v1",json={
        'token' : token
    })
    assert response.status_code == 200
    assert response.json() == {}
    assert check_valid_token(token) is None

def test_invalidate_token_one_user():
    response_data = register_valid_user()
    token = response_data['token']
    logout_valid_user(token)
    

def test_logout_multiple_users():
    response_data = register_valid_user()
    response_data1 = register_valid_user(email = 'validemail1@gmail.com',password= '123abc!@#1')
    response_data2 = register_valid_user(email = 'validemail2@gmail.com',password= '123abc!@#2')
    response_data3 = register_valid_user(email = 'validemail3@gmail.com',password= '123abc!@#3')
    response_data4 = register_valid_user(email = 'validemail4@gmail.com',password= '123abc!@#4')
    logout_valid_user(response_data2['token'])
    response_data5 = login_valid_user(email = 'validemail2@gmail.com',password= '123abc!@#2')
    assert isinstance(check_valid_token(response_data5['token']),dict)
    logout_valid_user(response_data5['token'])
    logout_valid_user(response_data4['token'])
    logout_valid_user(response_data3['token'])
    logout_valid_user(response_data2['token'])
    logout_valid_user(response_data1['token'])
    logout_valid_user(response_data['token'])


#note this gives an invalid token message with not logged in bro message on the test site
def test_logout_twice():
    response_data = register_valid_user()
    logout_valid_user(response_data['token'])
    logout_invalid_user(response_data['token'])
    