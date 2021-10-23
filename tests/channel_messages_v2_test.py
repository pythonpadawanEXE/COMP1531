from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests



BASE_URL = config.url

@pytest.fixture(autouse=True)
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}


def register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
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

#user for private channel
@pytest.fixture
def priv_chan_endpoint():
    other.clear_v1()
    token = (register_valid_user())['token']
    return (token, 'My Channel', False)

#user public channel 
@pytest.fixture
def pub_chan_endpoint():
    other.clear_v1()
    token = (register_valid_user())['token']
    return (token, 'My Channel', True)


#create multiple messages in a public channel
@pytest.fixture
def create_messages_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    for i in range(5):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : new_channel['channel_id'],
        'message' : Message
    })
    return new_channel,token

@pytest.fixture
def create_52_messages_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    for i in range(52):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : new_channel['channel_id'],
        'message' : Message
    })
    return new_channel,token

def channel_messages_endpoint(token,channel_id,start):
    response = requests.get(f"{BASE_URL}/channel/messages/v2",params={
        'token' : token,
        'channel_id' : channel_id,
        'start' : start
    })
    return response.json(),response.status_code

def create_channel_endpoint(token,name,is_public):
    response = requests.post(f"{BASE_URL}/channels/create/v2",json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })
    assert response.status_code == 200 
    return response.json()

"""
Valid Input
"""

#start is not greater than the total number of messages in the channel

def test_valid_start_index_1_endpoint(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    print(f"new_channel var {new_channel}")
    result,status_code = channel_messages_endpoint(token,new_channel['channel_id'],1)
    assert status_code == 200
    assert result["end"] == -1

def test_valid_start_index_2_endpoint(create_52_messages_endpoint):
    new_channel,token = create_52_messages_endpoint
    print(f"new_channel var {new_channel}")
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],1)
    assert status_code == 200

def test_invalid_start_index_3_endpoint(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],4)
    assert status_code == 200

"""
Input Errors
"""

#start is not less than 0
def test_invalid_negative_start_index_endpoint(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],-1) 
    assert status_code == 400



#channel_id does not refer to a valid channel

def test_invalid_channel_1_endpoint(pub_chan_endpoint):
    token, _, _ = pub_chan_endpoint
    _,status_code = channel_messages_endpoint(token,2,0) 
    assert status_code == 400


def test_invalid_empty_channel_2_endpoint(): 
    response_data = register_valid_user()
    _,status_code = channel_messages_endpoint(response_data['token'],2,0)
    assert status_code == 400

#start is greater than the total number of messages in the channel

def test_invalid_start_index_50_endpoint(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],50)
    assert status_code == 400

def test_invalid_start_index_5_endpoint(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],5)
    assert status_code == 400

#Channel ID is not valid or does not exist.
def test_invalid_channel_unexist_endpoint():
    is_public = True
    response_data = register_valid_user()
    create_channel_endpoint(response_data['token'],'NEw Channel',is_public)
    response_data = register_valid_user(email = "js2@email.com")
    _,status_code = channel_messages_endpoint(response_data['token'],10,0)
    assert status_code == 400

"""
Access Errors
"""
#Invalid Token
def test_invalid_empty_channel_1_endpoint():
    _,status_code = channel_messages_endpoint("token",2,0) 
    assert status_code == 403

#channel ID is private user channel messages is called with a user  that doesn't exist
def test_invalid_channel_private_endpoint():
    is_public = False
    response_data = register_valid_user()
    create_channel_endpoint(response_data['token'],'NEw Channel',is_public)
    response_data = register_valid_user(email = "js2@email.com")
    _,status_code = channel_messages_endpoint(response_data['token'],1,0)
    assert status_code == 403

#channel_id is valid and the authorised user is not a member of the channel

def test_not_member_of_channel_endpoint(priv_chan_endpoint):
    token, name, is_private = priv_chan_endpoint
    new_channel = create_channel_endpoint(token, name, is_private)
    response_data = register_valid_user(email = "js2@email.com")
    _,status_code = channel_messages_endpoint(response_data['token'],new_channel['channel_id'],0)
    assert status_code == 403

#channel_id is valid and the authorised user does not exist
def test_user_invalid_channel_endpoint(priv_chan_endpoint):
    token, name, is_private = priv_chan_endpoint
    new_channel = create_channel_endpoint(token, name, is_private)
    _,status_code = channel_messages_endpoint("token",new_channel['channel_id'],0)
    assert status_code == 403
