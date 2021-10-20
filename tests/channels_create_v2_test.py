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
    resp = requests.post(config.url + f"auth/register/v2",json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    user = json.loads(resp.text)
    return user

def test_channels_valid_create(setup):
    '''
    A simple test to check a valid channel creation
    '''
    user = setup
    channel = requests.post(config.url + 'channels/create/v2', json={'token': user['token'], 'name': 'My channel', 'is_public': 'True'})
    assert json.loads(channel.text) == {'channel_id': 1}

    # uncomment when channels/list/v2 complete
    list = requests.get(config.url + 'channels/list/v2', params={'token': user['token']})
    assert json.loads(list.text) == {'channels': [{'channel_id': json.loads(channel.text)['channel_id'], 'name': 'My channel'}]}

def test_bad_token(setup):
    channel = requests.post(config.url + 'channels/create/v2', json={'token': '', 'name': 'My channel', 'is_public': 'True'})
    assert channel.status_code == 403

def test_bad_name(setup):
    user = setup
    channel = requests.post(config.url + 'channels/create/v2', json={'token': user['token'], 'name': '', 'is_public': 'True'})
    assert channel.status_code == 400