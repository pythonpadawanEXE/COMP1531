# channels-listall-v1_test.py
# pytest file to test the implementation of channels_listall_v1

from src.error import AccessError
import pytest
import requests

from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_listall_v1
from src.other import clear_v1
from src import config

BASE_URL = config.url

@pytest.fixture
def setup():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

# Test all public channels from individual user
def test_listall_public_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    
    # List of channels that are public
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 2", True)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private channels from individual user
def test_listall_private_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    
    # List of channels that are private
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 1", False)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private and public channels from individual user
def test_listall_mixed_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    
    # List of channels that are private mixed with public channels
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all public channels from multiple users
def test_listall_public_multiple():
    clear_v1()

    # New user 1
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']

    # New user 2
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']
    
    # List of channels that are public
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 2", True)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 4", True)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 5", True)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 6", True)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private channels from multiple users
def test_listall_private_multiple():
    clear_v1()

    # New user 1
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']

    # New user 2
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']
    
    # List of channels that are private
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 1", False)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 3", False)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 4", False)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 5", False)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 6", False)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Test all private and public channels from multiple users
def test_listall_mixed_multiple():
    clear_v1()

    # New user 1
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']

    # New user 2
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']
    
    # List of channels that are private mixed with public channels
    list_of_channels = []
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 1", True)['channel_id'], 'name' : "Chan 1"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 2", False)['channel_id'], 'name' : "Chan 2"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_1, "Chan 3", True)['channel_id'], 'name' : "Chan 3"})

    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 4", False)['channel_id'], 'name' : "Chan 4"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 5", True)['channel_id'], 'name' : "Chan 5"})
    list_of_channels.append({'channel_id' : channels_create_v1(auth_user_id_2, "Chan 6", False)['channel_id'], 'name' : "Chan 6"})
    channels_dict = {'channels' : list_of_channels}

    # Get all channels
    channels = channels_listall_v1(auth_user_id_1)

    # Loop through created channels
    for channel in channels_dict['channels']:
        # Check if the channel exists
        assert(channel in channels['channels'])

# Invalid user
def test_raise_exception():
    clear_v1()
    with pytest.raises(AccessError):
        assert(channels_listall_v1(1234) == {})