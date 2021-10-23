import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates a user
    '''
    requests.delete(config.url + 'clear/v1')
    resp1 = requests.post(config.url + f"auth/register/v2",json={
        'email' : 'he@gmail.com',
        'password' : 'he123!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    creator = json.loads(resp1.text)
    
    resp2 = requests.post(config.url + f"auth/register/v2",json={
        'email' : 'lw@gmail.com',
        'password' : 'lh123!@#',
        'name_first' : 'Lewis',
        'name_last' : 'Hamilton'
    })
    user1 = json.loads(resp2.text)
    u_ids = [user1['auth_user_id']]

    resp3 = requests.post(config.url + f"auth/register/v2",json={
        'email' : 'cl@gmail.com',
        'password' : 'cl123!@#',
        'name_first' : 'Charles',
        'name_last' : 'Leclerc'
    })
    user2 = json.loads(resp3.text)
    u_ids.append(user2['auth_user_id'])

    return (creator, u_ids)

def test_dms_valid_create(setup):
    '''
    A simple test to check a valid channel creation
    '''
    creator, u_ids = setup
    dm = requests.post(config.url + 'dm/create/v1', json={'token': creator['token'], 'u_ids' : u_ids})
    assert json.loads(dm.text) == {'dm_id': 1}

def test_bad_token(setup):
    u_ids = setup[1]
    dm = requests.post(config.url + 'dm/create/v1', json={'token': '', 'u_ids' : u_ids})
    assert dm.status_code == 403

def test_bad_uids(setup):
    creator = setup[0]
    dm = requests.post(config.url + 'dm/create/v1', json={'token': creator['token'], 'u_ids' : [3,4]})
    assert dm.status_code == 400
