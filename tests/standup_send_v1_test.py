import pytest
import requests
import json
from time import sleep
from src import config

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(config.url + "clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users token
    '''

    response = requests.post(config.url + "auth/register/v2",json={
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last
    })

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data

def channels_create(token, name, is_public):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.post(config.url + "channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_join(token, channel_id):

    '''
    Joins a channel for user with given token and channel ID
    '''

    response = requests.post(config.url + "channel/join/v2", json={
        'token' : token,
        'channel_id' : channel_id
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data


@pytest.fixture
def setup():
    users = []
    users.append(register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter'))
    users.append(register_user('b@email.com', 'Pass123456!', 'Seth', 'Tilley'))
    channel = channels_create(users[0]['token'], "My channel", True)
    return (users, channel)

def standup_start(token, channel_id, length):
    '''
    Starts a standup in a given channel lasting a given length of time
    '''
    
    response = requests.post(config.url + "standup/start/v1", json={
        'token' : token,
        'channel_id' : channel_id,
        'length' : length
    })
    
    assert response.status_code == 200
    response_data = response.json()['time_finish']
    return response_data

def standup_active(token, channel_id):
    '''
    If standup active returns is_active and time until standup finishes, else None
    '''
    
    response = requests.get(config.url + "standup/active/v1", params={
        'token' : token,
        'channel_id' : channel_id
    })
    
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def standup_send(token, channel_id, message):
    '''
    Sends message in the active standup
    '''
    
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    
    assert response.status_code == 200
    
# Tests
    
def test_invalid_channel_id(setup):
    users, channel = setup
    standup_start(users[0]['token'], channel['channel_id'], 3)
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : users[0]['token'],
        'channel_id' : 999,
        'message' : "Invalid Channel"
    })
    
    assert response.status_code == 400

def test_message_too_long(setup):
    users, channel = setup
    standup_start(users[0]['token'], channel['channel_id'], 3)
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : users[0]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "a"*1001
    })
    
    assert response.status_code == 400

def test_standup_not_active(setup):
    users, channel = setup
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : users[0]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "Not Active"
    })
    
    assert response.status_code == 400
    

def test_user_not_channel_member(setup):
    users, channel = setup
    standup_start(users[0]['token'], channel['channel_id'], 3)
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : users[1]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "Not Channel Member"
    })
    
    assert response.status_code == 403

def test_bad_token(setup):
    users, channel = setup
    standup_start(users[0]['token'], channel['channel_id'], 3)
    response = requests.post(config.url + "standup/send/v1", json={
        'token' : "",
        'channel_id' : channel['channel_id'],
        'message' : "Bad Token"
    })
    
    assert response.status_code == 403
    
def test_valid_send(setup):
    users, channel = setup
    channel_join(users[1]['token'], channel['channel_id'])
    
    _ = standup_start(users[0]['token'], channel['channel_id'], 10)
    
    standup_send(users[0]['token'], channel['channel_id'], "A")
    standup_send(users[1]['token'], channel['channel_id'], "B")
    
    sleep(10)
    assert standup_active(users[0]['token'], channel['channel_id'])['is_active'] == False
    
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={
        'token': users[0]['token'],
        'channel_id': channel['channel_id'],
        'start': 0
    })
    messages = json.loads(channel_messages.text)['messages']
    assert messages[0]['message'] == f"jadepainter: A\nsethtilley: B"