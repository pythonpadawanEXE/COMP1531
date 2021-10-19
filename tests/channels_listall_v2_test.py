# channels_listall_v2_test.py
# pytest file to test the implementation of channels_listall_v2 endpoint

import pytest
import requests
from src import config
from src.error import AccessError

BASE_URL = config.url

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users token
    '''

    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last
    })

    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['user_token'],int)
    return response_data['token']

def channels_create(token, name, is_public):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.post(f"{BASE_URL}/channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channels_listall(token):
    '''
    Returns all the channels
    '''

    response = requests.get(f"{BASE_URL}/channels/listall/v2?{token}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Test all public channels from individual user
def test_listall_public_individual():
    # New user
    user_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    
    # List of channels that are public
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 2", True)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private channels from individual user
def test_listall_private_individual():
    # New user
    user_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['user_token']
    
    # List of channels that are private
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 1", False)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private and public channels from individual user
def test_listall_mixed_individual():
    # New user
    user_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['user_token']
    
    # List of channels that are private mixed with public channels
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all public channels from multiple users
def test_listall_public_multiple():
    # New user 1
    user_token_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['user_token']

    # New user 2
    user_token_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['user_token']
    
    # List of channels that are public
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 2", True)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 4", True)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 5", True)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 6", True)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private channels from multiple users
def test_listall_private_multiple():
    # New user 1
    user_token_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['user_token']

    # New user 2
    user_token_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['user_token']
    
    # List of channels that are private
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 1", False)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 4", False)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 5", False)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 6", False)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private and public channels from multiple users
def test_listall_mixed_multiple():
    # New user 1
    user_token_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['user_token']

    # New user 2
    user_token_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['user_token']
    
    # List of channels that are private mixed with public channels
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create(user_token_1, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 4", False)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 5", True)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create(user_token_2, "Chan 6", False)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall(user_token_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Invalid user
def test_raise_exception():
    response = requests.get(f"{BASE_URL}/channels/listall/v2?{1234}")
    assert response.status_code == 403