# admin_user_remove_v1_test.py
# pytest file to test the implementation of admin_user_remove_v1
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users.
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

def test_user_not_global_owner(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', params={'token': users[1]['token'], 'u_id': users[2]['auth_user_id']})
    assert resp.status_code == 403

def test_u_id_not_valid(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', params={'token': users[0]['token'], 'u_id': 7896})
    assert resp.status_code == 400

def test_u_id_only_global_owner(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', params={'token': users[0]['token'], 'u_id': users[0]['auth_user_id']})
    assert resp.status_code == 400

def test_valid_removal(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', params={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    assert resp.status_code == 200