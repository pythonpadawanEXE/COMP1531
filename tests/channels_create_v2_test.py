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
    resp = requests.post(config.url + 'auth/register/v2', params={'email': 'a@email.com', 'password': 'ASmith123654', 'name_first': 'Adam', 'name_last': 'Smith'})
    user = json.loads(resp.text)
    return user

def test_channels_valid_create(setup):
    '''
    A simple test to check a valid channel creation
    '''
    user = setup
    channel = requests.get(config.url + 'channels/create/v2', params={'token': user['token'], 'name': 'My channel', 'is_public': 'True'})
    assert json.loads(channel.text) == {'channel_id': 1}

    list = requests.get(config.url + 'channels/list/v2', params={'token': user['token']})
    assert json.loads(list.text) == {'channels': [{'channel_id': 1, 'name': 'My channel'}]}

def test_bad_token(setup):
    channel = requests.get(config.url + 'channels/create/v2', params={'token': '685412', 'name': 'My channel', 'is_public': 'True'})
    assert channel.status_code == 402
    pass

def test_bad_name(setup):
    user = setup
    channel = requests.get(config.url + 'channels/create/v2', params={'token': user['token'], 'name': '', 'is_public': 'True'})
    assert channel.status_code == 400
    pass