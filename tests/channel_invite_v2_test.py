# channel_invite_v2_test.py
# pytest file to test the implementation of channel/invite/v2
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users and channels.
    '''
    user = []
    channels = []
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
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail2@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Jade',
        'name_last' : 'Painter'
    })
    user.append(json.loads(resp.text))
    chan_0 = requests.post(config.url + 'channels/create/v2', json={'token': user[0]['token'], 'name': 'My channel', 'is_public': 'True'})
    channels.append(json.loads(chan_0.text))
    chan_1 = requests.post(config.url + 'channels/create/v2', json={'token': user[1]['token'], 'name': 'My private channel', 'is_public': 'False'})
    channels.append(json.loads(chan_1.text))
    return (user, channels)

def test_invalid_channel_id(setup):
    users, _ = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': users[0]['token'], 'channel_id': 1234, 'u_id': users[1]['auth_user_id']})
    assert resp.status_code == 400

def test_invalid_u_id(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': users[0]['token'], 'channel_id': channels[0]['channel_id'], 'u_id': 999})
    assert resp.status_code == 400

def test_u_id_a_member(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': users[0]['token'], 'channel_id': channels[0]['channel_id'], 'u_id': users[0]['auth_user_id']})
    assert resp.status_code == 400

def test_auth_user_not_member(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': users[1]['token'], 'channel_id': channels[0]['channel_id'], 'u_id': users[2]['auth_user_id']})
    assert resp.status_code == 403

def test_bad_auth_user_id(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': '', 'channel_id': channels[0]['channel_id'], 'u_id': users[2]['auth_user_id']})
    assert resp.status_code == 403

def test_valid_invite(setup):
    users, channels = setup
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': users[0]['token'], 'channel_id': channels[0]['channel_id'], 'u_id': users[2]['auth_user_id']})
    assert resp.status_code == 200
