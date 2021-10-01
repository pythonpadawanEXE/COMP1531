# channels-listall-v1_test.py
# pytest file to test the implementation of channels_listall_v1

# test

from src.error import AccessError
import pytest

from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_listall_v1
from src.other import clear_v1

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

# Test all private channels from individual user
def test_listall_private_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']

# Test all public channels from multiple users
def test_listall_public_multiple():
    clear_v1()

# Test all private channels from multiple users
def test_listall_private_multiple():
    clear_v1()

def test_raise_exception(): 
    clear_v1()
    with pytest.raises(AccessError):
        assert(channels_listall_v1(687543) == {})