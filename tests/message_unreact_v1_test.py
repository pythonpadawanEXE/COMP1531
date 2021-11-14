import pytest
import requests
from src import config
from tests.helper_test_funcs import remove_message_endpoint
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

def message_react(token, message_id, react_id):
    response = requests.post(config.url + "message/react/v1", json={
        'token' : token,
        'message_id' : message_id,
        'react_id' : react_id
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def message_unreact(token, message_id, react_id):
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : token,
        'message_id' : message_id,
        'react_id' : react_id
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

@pytest.fixture
def setup():
    users = []
    users.append(register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter'))
    users.append(register_user('b@email.com', 'Pass123456!', 'Seth', 'Tilley'))
    users.append(register_user('c@email.com', 'Pass123456!', 'Hannah', 'Buttsworth'))
    channel = channels_create(users[0]['token'], "My channel", True)
    channel_join(users[1]['token'], channel['channel_id'])
    #channel_join(users[2]['token'], channel['channel_id'])
    dm = dm_create(users[0]['token'], [users[1]['auth_user_id']])
    return (users, channel, dm)

# Tests

# message_id is not a valid message within a channel or DM that the authorised user has joined
def test_invalid_message_id(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    # User 1 reacts to the message
    message_react(users[1]['token'], id, 1)

    # User 1 tries to unreact to the message but message is wrong ID
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : users[1]['token'],
        'message_id' : id + 1,
        'react_id' : 1
    })

    assert response.status_code == 400

# message_id is not a valid message within a channel or DM that the authorised user has joined (Channel)
def test_user_not_in_channel(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    # User 1 reacts to the message
    message_react(users[1]['token'], id, 1)

    # User 1 tries to unreact to the message but message is wrong ID
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : users[2]['token'],
        'message_id' : id,
        'react_id' : 1
    })

    assert response.status_code == 400

# message_id is not a valid message within a channel or DM that the authorised user has joined (DM)
def test_user_not_in_dm(setup):
    users, _, dm = setup

    # User 0 creates a message in DM
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']

    # User 1 reacts to the message
    message_react(users[1]['token'], id, 1)

    # User 2 tries to unreact to the message but user is not in DM
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : users[2]['token'],
        'message_id' : id,
        'react_id' : 1
    })

    assert response.status_code == 400

# react_id is not a valid react ID
def test_invalid_react_id(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    # User 1 reacts to the message
    message_react(users[1]['token'], id, 1)

    # User 1 tries to unreact to the message but react is wrong ID
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : users[1]['token'],
        'message_id' : id,
        'react_id' : 2
    })

    assert response.status_code == 400

# the message does not contain a react with ID react_id from the authorised user
def test_message_not_contain_react_id(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    # User 1 tries to unreact to the message but the react_id is not a react_id from the authorised user
    response = requests.post(config.url + "message/unreact/v1", json={
        'token' : users[1]['token'],
        'message_id' : id,
        'react_id' : 1
    })

    assert response.status_code == 400

def test_valid_unreact_in_channel(setup):
    users, channel, _ = setup
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']
    _ = message_react(users[1]['token'], id, 1)
    message_unreact(users[1]['token'], id, 1)

def test_valid_react_in_dm(setup):
    users, _, dm = setup
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']
    _ = message_react(users[1]['token'], id, 1)
    _ = message_react(users[0]['token'], id, 1)
    message_unreact(users[0]['token'], id, 1)
    message_unreact(users[1]['token'], id, 1)

def test_message_react_remove(setup):
    users, _, dm = setup
    message_dm(users[0]['token'], dm['dm_id'], "Howdy2")
    id = message_dm(users[0]['token'], dm['dm_id'], "Howdy")['message_id']
    _ = message_unreact(users[1]['token'], id, 1)
    remove_message_endpoint(users[0]['token'],id)
    _ = message_unreact(users[0]['token'], id, 1)
