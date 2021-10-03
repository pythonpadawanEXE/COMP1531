from src import auth
import re
import pytest
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src import other
from src import channels
from src import channel

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

@pytest.fixture
def create_messages(pub_chan):
    id, name, is_public = pub_chan
    new_channel = channels.channels_create_v1(id, name, is_public)
    store = data_store.get()
    for i in range(5):
        Message = "message" + str(i)
        channel.create_message_v1(id,new_channel['channel_id'],Message)
    return new_channel,id

"""
Valid Input
"""

#start is not greater than the total number of messages in the channel

def test_valid_start_index(create_messages):
    new_channel,id = create_messages
    store = data_store.get()
    channels_ = store['channels']
    print(channels_)

 
    result = channel.channel_messages_v1(id,new_channel['channel_id'],1)
    print(result)
    assert result["end"] == -1
"""
Input Errors
"""

#channel_id does not refer to a valid channel

def test_invalid_channel_1(pub_chan):
    id, name, is_public = pub_chan
    
    store = data_store.get()
    channels_ = store['channels']
    print(channels_)
    
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(id,2,0)

def test_invalid_empty_channel_1():
    other.clear_v1()   
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(1,2,0)

def test_invalid_empty_channel_2():
    other.clear_v1()   
    auth_user_id = auth.auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(1,2,0)

#start is greater than the total number of messages in the channel

def test_invalid_start_index(create_messages):
    new_channel,id = create_messages
    
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(id,new_channel['channel_id'],50)

#Channel ID is not valid or does not exist.
def test_invalid_channel_unexist():
    other.clear_v1()
    is_public = True
    auth_user_id = auth.auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    channels.channels_create_v1(auth_user_id,'New Channel', is_public)
    auth_user_id = auth.auth_register_v1("js2@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(1,10,0)

def test_invalid_channel_private():
    other.clear_v1()
    is_public = False
    auth_user_id = auth.auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    channels.channels_create_v1(auth_user_id,'New Channel', is_public)
    auth_user_id = auth.auth_register_v1("js2@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    with pytest.raises(InputError):
        result = channel.channel_messages_v1(2,5,0)
"""
Access Errors
"""
#channel_id is valid and the authorised user is not a member of the channel

def test_not_member_of_channel(priv_chan):
    id, name, is_private = priv_chan
    new_channel = channels.channels_create_v1(id, name, is_private)

    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    with pytest.raises(AccessError):
        result = channel.channel_messages_v1(result['auth_user_id'],new_channel['channel_id'],0)


#channel_id is valid and the authorised user does not exist
def test_user_invalid_channel(priv_chan):
    id, name, is_private = priv_chan
    new_channel = channels.channels_create_v1(id, name, is_private)
    with pytest.raises(AccessError):
        result = channel.channel_messages_v1(2,new_channel['channel_id'],0)

