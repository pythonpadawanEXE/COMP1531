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

def message_share(token, og_message_id, message, channel_id, dm_id):
    response = requests.post(config.url + "message/share/v1", json={
        'token' : token,
        'og_message_id' : og_message_id,
        'message' : message,
        'channel_id' : channel_id,
        'dm_id' : dm_id
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
    dm = dm_create(users[0]['token'], [users[1]['auth_user_id']])
    return (users, channel, dm)

# the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid)
# and the authorised user has not joined the channel or DM they are trying to share the message to
def valid_channel_dm_id_not_member(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']

    response = requests.post(config.url + "message/share/v1", json={
        'token' : users[2]['token'],
        'og_message_id' : og_message_id,
        'message' : "I am sharing this MSG",
        'channel_id' : channel_id,
        'dm_id' : -1
    })

    assert response.status_code == 403

# both channel_id and dm_id are invalid
def invalid_channel_dm_id(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']

    response = requests.post(config.url + "message/share/v1", json={
        'token' : users[1]['token'],
        'og_message_id' : og_message_id,
        'message' : "I am sharing this MSG",
        'channel_id' : 99,
        'dm_id' : 99
    })

    assert response.status_code == 400

# neither channel_id nor dm_id are -1
def invalid_channel_dm_id_2(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']

    response = requests.post(config.url + "message/share/v1", json={
        'token' : users[1]['token'],
        'og_message_id' : og_message_id,
        'message' : "I am sharing this MSG",
        'channel_id' : 1,
        'dm_id' : 1
    })

    assert response.status_code == 400
        
# og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def invalid_og_message_id(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']

    response = requests.post(config.url + "message/share/v1", json={
        'token' : users[1]['token'],
        'og_message_id' : og_message_id + 1,
        'message' : "I am sharing this MSG",
        'channel_id' : channel_id,
        'dm_id' : -1
    })

    assert response.status_code == 400

# length of message is more than 1000 characters
def invalid_message_length(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']

    response = requests.post(config.url + "message/share/v1", json={
        'token' : users[1]['token'],
        'og_message_id' : og_message_id,
        'message' : "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sit amet aliquet neque. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla eget dui sit amet erat tempus lobortis quis vitae dui. Donec quis mattis velit, ac tempus orci. Pellentesque id mi eget dui tempor tempor. Suspendisse quis consectetur augue, non eleifend orci. Mauris non imperdiet nunc, non molestie metus. Morbi hendrerit feugiat nibh vitae tempor. Etiam neque turpis, condimentum ac diam vitae, faucibus ultricies nunc. Phasellus laoreet vel enim ut vehicula. Phasellus hendrerit arcu a eros tincidunt vulputate ut et nulla. Maecenas viverra vitae lectus at ultricies. In facilisis erat congue lacinia consequat. Etiam vel faucibus nunc. Vivamus consequat eros ac nibh accumsan, a placerat dolor varius. Duis vel augue nunc. Pellentesque vulputate aliquam finibus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Cras eget orci lacinia, pretium lorem ac,",
        'channel_id' : channel_id,
        'dm_id' : -1
    })

    assert response.status_code == 400

def valid_message_share(setup):
    users, channel_id, dm_id = setup

    og_message_id = message_channel(users[1]['token'], channel_id, "First!!!")['message_id']
    message_share(users[1]['token'], og_message_id, "I am sharing this MSG", channel_id, -1)