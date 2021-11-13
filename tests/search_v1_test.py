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

def message_search(token, query):
    response = requests.get(f"{config.url}search/v1?token={token}&query_str={query}")
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

def test_invalid_search(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    response = requests.get(f"{config.url}search/v1?token={users[0]['token']}&query_str={''}")
    assert response.status_code == 400

    response = requests.get(f"{config.url}search/v1?token={users[0]['token']}&query_str={'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum volutpat nulla massa, in laoreet magna blandit id. Vivamus vitae magna sit amet lorem commodo tincidunt sed id risus. Pellentesque finibus mollis efficitur. Ut id risus eget justo rhoncus feugiat. Vivamus commodo urna id augue placerat vestibulum in ut sapien. Phasellus tempus dignissim finibus. Nullam nulla velit, lobortis eu auctor ut, faucibus id risus. Donec non erat quam. Cras accumsan a mi eu pellentesque. Nullam ultricies egestas commodo. Morbi gravida risus at condimentum auctor. Suspendisse mi quam, ultrices eget rhoncus et, sodales vitae lacus. Nam sed mattis massa, ac fringilla nulla. Nam sed imperdiet augue. Sed eu velit nisl. Quisque dignissim nulla sodales sem pellentesque. Nullam ultricies egestas commodo. Morbi gravida risus at condimentum auctor. Suspendisse mi quam, ultrices eget rhoncus et, sodales vitae lacus. Nam sed mattis massa, ac fringilla nulla. Nam sed imperdiet augue. Sed eu velit nisl. Quisque dignissim nulla sodales sem'}")
    assert response.status_code == 400

def test_valid_search(setup):
    users, channel, _ = setup

    # User 0 creates a message
    id = message_channel(users[0]['token'], channel['channel_id'], "Howdy")['message_id']

    # Search with query how
    response_data = message_search(users[1]['token'], "how")['messages']
    assert response_data[0]['message'] == 'Howdy'