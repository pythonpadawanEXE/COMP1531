# admin_userpermission_change_v1_test.py
# pytest file to test the implementation of admin/userpermission/change/v1
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

def test_u_id_invalid(setup):
    users = setup
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[0]['token'], 'u_id': 123, 'permission_id': 1})
    assert resp.status_code == 400

def test_attempt_to_demote_only_global_owner(setup):
    users = setup
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[0]['token'], 'u_id': users[0]['auth_user_id'], 'permission_id': 2})
    assert resp.status_code == 400

def test_invalid_permission_id(setup):
    users = setup
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[0]['token'], 'u_id': users[1]['auth_user_id'], 'permission_id': 5})
    assert resp.status_code == 400

def test_auth_user_not_global_owner(setup):
    users = setup
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[1]['token'], 'u_id': users[2]['auth_user_id'], 'permission_id': 1})
    assert resp.status_code == 403

def test_valid_promote_and_demote(setup):
    users = setup
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[0]['token'], 'u_id': users[1]['auth_user_id'], 'permission_id': 1})
    assert resp.status_code == 200
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={'token': users[1]['token'], 'u_id': users[0]['auth_user_id'], 'permission_id': 2})
    assert resp.status_code == 200
