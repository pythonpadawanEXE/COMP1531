from src import auth
import re
import pytest
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src import other
from src import channels

#create private channel
@pytest.fixture
def priv_chan():
    other.clear_v1()
    auth_user_id = auth.auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    return (auth_user_id, 'My Channel', False)


@pytest.fixture
def pub_chan():
    other.clear_v1()
    auth_user_id = auth.auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    return (auth_user_id, 'My Channel', True)

"""
Valid Input
"""

#start is not greater than the total number of messages in the channel

def valid_start_index_test(pub_chan):
    other.clear_v1()
    id, name, is_public = pub_chan
    new_channel = channels.channels_create_v1(id, name, is_public)
    #hard code some messages
    
    with pytest.raises(InputError):
        result = channels.channel_messages_v1(id,new_channel,1)
"""
Input Errors
"""

#channel_id does not refer to a valid channel

def invalid_channel_test_1(pub_chan):
    other.clear_v1()
    id, name, is_public = pub_chan
    new_channel = channels.channels_create_v1(id, name, is_public)

    
    with pytest.raises(InputError):
        result = channels.channel_messages_v1(id,2,0)

def invalid_channel_test_1():
    other.clear_v1()
    with pytest.raises(InputError):
        result = channels.channel_messages_v1(1,2,0)

#start is greater than the total number of messages in the channel

def invalid_start_index_test():
    other.clear_v1()
    id, name, is_public = pub_chan
    new_channel = channels.channels_create_v1(id, name, is_public)
    #hard code some messages
    
    with pytest.raises(InputError):
        result = channels.channel_messages_v1(0,0,50)



"""
Access Errors
"""
#channel_id is valid and the authorised user is not a member of the channel

def invalid_start_index_test(priv_chan):
    other.clear_v1()
    id, name, is_private = priv_chan
    new_channel = channels.channels_create_v1(id, name, is_private)

    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    with pytest.raises(AccessError):
        result = channels.channel_messages_v1(result['auth_user_id'],new_channel['channel_id'],0)


#channel_id is valid and the authorised user does not exist
def invalid_start_index_test(priv_chan):
    other.clear_v1()
    id, name, is_private = priv_chan
    new_channel = channels.channels_create_v1(id, name, is_private)
    with pytest.raises(AccessError):
        result = channels.channel_messages_v1(2,new_channel['channel_id'],0)