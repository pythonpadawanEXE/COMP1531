import pytest
import requests
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

def message_channel(token, channel_id, message):
    response = requests.post(config.url + "message/send/v1", json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_create(token, u_ids):
    response = requests.post(config.url + 'dm/create/v1', json={
        'token': token,
        'u_ids' : u_ids
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def message_dm(token, dm_id, message):
    response = requests.post(config.url + "message/senddm/v1", json={
        'token' : token,
        'dm_id' : dm_id,
        'message' : message
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def message_pin(token, message_id):
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : token,
        'message_id' : message_id
    })

    
    return response.json(),response.status_code

@pytest.fixture
def setup():
    users = []
    users.append(register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter'))
    users.append(register_user('b@email.com', 'Pass123456!', 'Seth', 'Tilley'))
    users.append(register_user('c@email.com', 'Pass123456!', 'Hannah', 'Buttsworth'))
    channel = channels_create(users[0]['token'], "My channel", True)
    channel_join(users[1]['token'], channel['channel_id'])
    dm = dm_create(users[0]['token'], [users[1]['auth_user_id']])
    return (users, channel, dm)

# Tests
'''
Valid Input
'''
def test_valid_pin_in_channel(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    _,status_code = message_pin(users[0]['token'], id)
    
    assert status_code == 200

def test_valid_pin_in_dm(setup):
    users, _, dm = setup
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']
    _,status_code = message_pin(users[0]['token'], id)
    assert status_code == 200


'''
Input Error
'''
#no valid message_id i.e. message doesn't exist
def test_message_id_not_exist(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : users[1]['token'],
        'message_id' : id + 1,

    })

    assert response.status_code == 400

def test_message_id_not_valid_in_channel(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : users[2]['token'],
        'message_id' : id,
    })

    assert response.status_code == 400

def test_message_id_not_valid_in_dm(setup):
    users, _, dm = setup
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : users[2]['token'],
        'message_id' : id,

    })

    assert response.status_code == 400

def test_already_pinned(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    _,_ = message_pin(users[0]['token'], id)
    _,status_code = message_pin(users[0]['token'], id)
    assert status_code == 400


'''
Access Error
'''


def test_not_channel_owner(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    _,status_code = message_pin(users[1]['token'], id)
    assert status_code == 403

def test_not_dm_owner(setup):
    users, _, dm = setup
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : users[1]['token'],
        'message_id' : id,

    })

    assert response.status_code == 403

def test_invalid_token(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    response = requests.post(config.url + "message/pin/v1", json={
        'token' : "",
        'message_id' : id,
    })

    assert response.status_code == 403




