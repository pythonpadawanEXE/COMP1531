from src import auth,other,config
import re
import pytest
from src.error import InputError,AccessError
import requests
from src.data_store import data_store

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

'''
Valid Input
'''
#test for standard login
'''
def test_valid_login_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)
    print(data_store.get())
'''
def test_valid_login_1_endpoint():
    response_data = register_valid_user()
    assert response_data['auth_user_id'] == 0
    response_data = login_valid_user()
    assert response_data['auth_user_id'] == 0
    print(data_store.get())

def test_valid_login_2_endpoint():
    response_data = register_valid_user()
    assert response_data['auth_user_id'] == 0
    response_data = login_valid_user()
    assert response_data['auth_user_id'] == 0
    print(data_store.get())