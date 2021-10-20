# channels_details_v2_test.py
# pytest file to test the implementation of channel_details_v2 endpoint

import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(f"{BASE_URL}clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users uid and token
    '''

    response = requests.post(f"{BASE_URL}auth/register/v2",json={
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

    response = requests.post(f"{BASE_URL}channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_join(token, channel_id):

    '''
    Adds a user with token to channel with ID channel_id
    '''

    response = requests.post(f"{BASE_URL}channel/join/v2", json={
        'token' : token,
        'channel_id' : channel_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_details(token, channel_id):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.get(f"{BASE_URL}channel/details/v2?token={token}&channel_id={channel_id}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Test for a single member with a public channel
def test_details_public_individual():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']
    auth_user_id = user['auth_user_id']
    # Channel ID
    channel_id = channels_create(token, "Chan 1", True)['channel_id']
    # Channel details
    details = channel_details(token, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(auth_user_id == user['u_id'])

# Test for a single member with a private channel
def test_details_private_individual():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']
    auth_user_id = user['auth_user_id']
    # Channel ID
    channel_id = channels_create(token, "Chan 1", False)['channel_id']
    # Channel details
    details = channel_details(token, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(auth_user_id == user['u_id'])

# Test for a single member with public and private channels
def test_details_mixed_individual():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']
    auth_user_id = user['auth_user_id']
    # Channel ID
    channel_id = channels_create(token, "Chan 1", False)['channel_id']
    # Create a public channel
    channels_create(token, "Chan 2", True)['channel_id']
    # Channel details
    details = channel_details(token, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(auth_user_id == user['u_id'])


# Test for multiple members with a public channel
def test_details_public_multiple():
    # New user
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']
    auth_user_id_1 = user_1['auth_user_id']

    # New user 2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']
    auth_user_id_2 = user_2['auth_user_id']

    # Channel ID
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']
    # Invite auth_user_id_2 to channel
    channel_join(token_2, channel_id)
    # Channel details
    channel_details = channel_details(token_1, channel_id)

    # Loop through the channel details and find if auth_user_id and auth_user_id2 is in the channel
    for user in channel_details['all_members']:
        assert(auth_user_id_1 == user['u_id'] or auth_user_id_2 == user['u_id'])


# Test for invalid channel ID
def test_invalid_channel():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']

    response = requests.get(f"{BASE_URL}channel/details/v2?token={token}&channel_id={9999}")
    assert response.status_code == 400

# Test for valid channel ID and the authorised user is not a member of the channel
def test_user_unauthorised():
    # New user
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']
    # New user 2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']
    # Channel ID
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    response = requests.get(f"{BASE_URL}channel/details/v2?token={token_2}&channel_id={channel_id}")
    assert response.status_code == 403