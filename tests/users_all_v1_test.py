# userss_all_v1_test.py
# pytest file to test the implementation of userss_all_v1
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
    channels = []
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
    chan_0 = requests.post(config.url + 'channels/create/v2', json={'token': users[0]['token'], 'name': 'My channel', 'is_public': 'True'})
    channels.append(json.loads(chan_0.text))
    chan_1 = requests.post(config.url + 'channels/create/v2', json={'token': users[1]['token'], 'name': 'My private channel', 'is_public': 'False'})
    channels.append(json.loads(chan_1.text))
    return (users, channels)

def test_invalid_token(setup):
    _ = setup
    resp = requests.get(config.url + 'users/all/v1', params={'token': ""})
    assert resp.status_code == 403

def test_valid_use(setup):
    users, channels = setup
    _ = requests.post(config.url + 'channel/join/v2', json={'token': users[1]['token'], 'channel_id': channels[0]['channel_id']})
    resp = requests.get(config.url + 'users/all/v1', params={'token': users[0]['token']})
    assert resp.status_code == 200
    response_data = resp.json()
    assert response_data == {
        'users' : [
            {
                'u_id' : users[0]['auth_user_id'],
                'email' : 'validemail@gmail.com',
                'name_first' : 'Hayden',
                'name_last' : 'Everest',
                'handle_str' : 'haydeneverest'
            }, 
            {
                'u_id' : users[1]['auth_user_id'],
                'email' : 'validemail2@gmail.com',
                'name_first' : 'Robert',
                'name_last' : 'Reid',
                'handle_str' : 'robertreid'
            }
        ]
    }
