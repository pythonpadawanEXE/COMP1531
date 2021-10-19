import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates a user
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

def test_valid_list(setup):
    users = setup
    channel1 = requests.post(config.url + 'channels/create/v2', json={'token': users[1]['token'], 'name': 'My channel', 'is_public': 'True'})
    channel2 = requests.post(config.url + 'channels/create/v2', json={'token': users[2]['token'], 'name': 'My 2nd channel', 'is_public': 'True'})

    list1 = requests.get(config.url + 'channels/list/v2', params={'token': users[1]['token']})
    assert json.loads(list1.text) == {'channels': [{'channel_id': json.loads(channel1.text)['channel_id'], 'name': 'My channel'}]}

    list2 = requests.get(config.url + 'channels/list/v2', params={'token': users[2]['token']})
    assert json.loads(list2.text) == {'channels': [{'channel_id': json.loads(channel2.text)['channel_id'], 'name': 'My 2nd channel'}]}

def test_bad_token(setup):
    channel1 = requests.post(config.url + 'channels/list/v2', json={'token': ""})
    assert channel1.status_code == 403
