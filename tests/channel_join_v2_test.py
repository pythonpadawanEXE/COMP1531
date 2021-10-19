# channel_join_v1_test.py
# pytest file to test the implementation of channel_join_v2
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users
    '''
    user = []
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    user.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail1@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'John',
        'name_last' : 'Smith'
    })
    user.append(json.loads(resp.text))
    return user


def test_invalid_channel_id():
    pass
        
def test_invalid_auth_user_id():
    pass
        
def test_already_joined():
    pass

def test_join_private_channel():
    pass

def test_join_public_channel():
    pass

def test_global_owner_join_private_channel():
    pass
