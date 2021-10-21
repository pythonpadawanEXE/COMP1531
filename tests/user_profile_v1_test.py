# user_profile_v1_test.py
# pytest file to test the implementation of user_profile_v1
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users and channels.
    '''
    users = []
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    users.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail2@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Robert',
        'name_last' : 'Reid'
    })
    users.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail3@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Jade',
        'name_last' : 'Painter'
    })
    users.append(json.loads(resp.text))
    return users

def test_invalid_token(setup):
    users = setup
    resp = requests.get(config.url + 'user/profile/v1', params={'token': "", 'u_id': users[0]['auth_user_id']})
    assert resp.status_code == 403

def test_invalid_u_id(setup):
    users = setup
    resp = requests.get(config.url + 'user/profile/v1', params={'token': users[0]['token'], 'u_id': 1032764})
    assert resp.status_code == 400

def test_valid_use(setup):
    users = setup
    resp = requests.get(config.url + 'user/profile/v1', params={'token': users[1]['token'], 'u_id': users[0]['auth_user_id']})
    assert resp.status_code == 200
    response_data = resp.json()
    assert response_data == {'u_id': users[0]['auth_user_id'], 'email': 'validemail@gmail.com', 'name_first': 'Hayden', 'name_last': 'Everest', 'handle_str': 'haydeneverest'}