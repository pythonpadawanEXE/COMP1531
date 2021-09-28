# channels-create-v1_test.py
# pytest file to test the implementation of channels_create_v1

import pytest

from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def chan1():
    clear_v1()
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    return (auth_user_id, 'My Channel', True)

@pytest.fixture
def invalid_chan1():
    clear_v1()
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    return (auth_user_id, '', True)

@pytest.fixture
def invalid_chan2():
    clear_v1()
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    return (auth_user_id, 'AAAAAAAAAAAAAAAAAAAAA', True)

def test_valid_creation(chan1):
    id, name, is_public = chan1
    new_channel = channels_create_v1(id, name, is_public)
    list_of_channels = channels_list_v1(id)
    assert(new_channel in list_of_channels)

# Test for InputError when name < 1 char long
def test_exception_too_short(invalid_chan1): 
    id, name, is_public = invalid_chan1
    with pytest.raises(InputError):
        assert(channels_create_v1(id, name, is_public) == 1)

# Test for InputError when name > 20 char long
def test_exception_too_long(invalid_chan2): 
    id, name, is_public = invalid_chan2
    with pytest.raises(InputError):
        assert(channels_create_v1(id, name, is_public) == 1)

def test_raise_AccessError(invalid_chan1): 
    id, name, is_public = invalid_chan1
    with pytest.raises(AccessError):
        assert(channels_create_v1(id, name, is_public) == {})