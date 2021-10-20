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
    message_ids = []
    for i in range(5):
        Message = "message" + str(i)
        message_id = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : new_channel['channel_id'],
        'message' : Message
        })
        message_ids.append[message_id]
    return new_channel,token,message_ids

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

def create_message_endpoint(token,channel_id,message):
    response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    return response.json(),response.status_code

def edit_message_endpoint(token,message_id,message):
    response = requests.put(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'message_id' : message_id,
        'message' : message
    })
    return response.json(),response.status_code

'''
Valid Input
'''

def test_valid_message_edit_endpoint(create_messages_endpoint):
    new_channel,token,message_ids =   create_messages_endpoint
    data,status_code =   edit_message_endpoint(token,message_ids[0],"Modified message.")
    assert status_code == 200
    assert data == {}


#If the new message is an empty string, the message is deleted.
def test_delete_short_message_endpoint(create_messages_endpoint)
    new_channel,token,message_ids =   create_messages_endpoint
    data,status_code =   edit_message_endpoint(token,message_ids[0],"")
    assert status_code == 200
    assert data = {}
    #test message is deleted
    data,status_code =   edit_message_endpoint(token,message_ids[0],"yes")
    assert status_code == 400


'''
Input Error
'''
long_msg = "l"
for i in range(1010):
    long_msg = long_msg + "o"
long_msg = long_msg + "ng"
#length of message is over 1000 characters
def test_invalid_long_message_endpoint(create_messages_endpoint)
    new_channel,token,message_ids =   create_messages_endpoint
    data,status_code =   edit_message_endpoint(token,message_ids[0],long_msg)
    assert status_code == 400

#message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_invalid_message_id_endpoint(create_messages_endpoint)
    new_channel,token,message_ids =   create_messages_endpoint
    data,status_code =   edit_message_endpoint(token,10,"NEw Msg")
    assert status_code == 400

'''
Access Error
'''
#editor is not an owner of channel or DM and not the maker of the message
def test_invalid_message_id_endpoint(create_messages_endpoint)
    new_channel,token,message_ids =   create_messages_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    data,status_code =   edit_message_endpoint(data['token'],message_ids[0],"NEw Msg")
    assert status_code == 400

