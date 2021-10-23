from src import auth,other,config
import re
import pytest
from src.error import InputError,AccessError
import requests
from src.data_store import data_store
from src.other import check_valid_token,decode_jwt,clear_v1

BASE_URL = config.url

@pytest.fixture(autouse=True)
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def token_validity_check_pytest(token,store):
    decoded_token = decode_jwt(token)
    users = store['users']
    for user in users:
        if user['u_id'] == decoded_token['auth_user_id']:
            for session_id in user['sessions']:
                if session_id == decoded_token['session_id']:
                    return {'auth_user_id':decoded_token['auth_user_id'],'session_id':decoded_token['session_id']}
    raise AccessError(description="Invalid Token")

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
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data


def logout_invalid_user(token):
    response = requests.post(f"{BASE_URL}/auth/logout/v1",json={
        'token' : token
    })
    assert response.status_code == 403


def logout_valid_user(token):
    response = requests.post(f"{BASE_URL}/auth/logout/v1",json={
        'token' : token
    })
    assert response.status_code == 200
    assert response.json() == {}
    store = (requests.get(f"{BASE_URL}/get_data")).json()
    with pytest.raises(AccessError):
        token_validity_check_pytest(token,store)
'''
Valid Input
'''
def test_invalidate_token_one_user(setup):
    response_data = register_valid_user()
    response_data = login_valid_user()
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
    store = (requests.get(f"{BASE_URL}/get_data")).json()
    assert isinstance(token_validity_check_pytest(response_data5['token'],store),dict)
    logout_valid_user(response_data5['token'])
    logout_valid_user(response_data4['token'])
    logout_valid_user(response_data3['token'])
    logout_invalid_user(response_data2['token'])
    logout_valid_user(response_data1['token'])
    logout_valid_user(response_data['token'])

'''
Access Error
'''
#note this gives an invalid token message with not logged in bro message on the test site
#second logout raises AccessError 403
def test_logout_twice():
    response_data = register_valid_user()
    logout_valid_user(response_data['token'])
    logout_invalid_user(response_data['token'])

def test_logout_Invalid_token_from_credidentials_cleared():
    _ = register_valid_user()
    _ = register_valid_user(email="jake@gmail.com")
    response_data2 = register_valid_user(email="jake1@gmail.com")
    response_data3 = login_valid_user(email="jake1@gmail.com")
    _  = requests.delete(f"{BASE_URL}/clear/v1")
    _ = register_valid_user()
    _ = register_valid_user(email="jake@gmail.com")
    logout_invalid_user(response_data2['token'])
    logout_invalid_user(response_data3['token'])

    