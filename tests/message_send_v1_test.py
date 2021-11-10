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

'''
Valid Input
'''
#Valid Message
def test_valid_send_message_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,new_channel['channel_id'],"Howdy Partner!")
    assert status_code == 200


def test_under_fifty_messages_sent(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)

    message_ids = [
        create_message_endpoint(token, new_channel['channel_id'], 'you are a toy')[0]['message_id'] for x in
        range(10)
    ]

    ch_msgs,_ = channel_messages_endpoint(token, new_channel['channel_id'], 0)

    assert ch_msgs['start'] == 0
    assert ch_msgs['end'] == -1
    assert message_ids[::-1] == [m['message_id'] for m in ch_msgs['messages']]

def test_over_fifty_messages_sent(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)

    message_ids = [
        create_message_endpoint(token, new_channel['channel_id'], 'you are a toy')[0]['message_id'] for x in
        range(51)
    ]
    message_ids.reverse()
    ch_msgs,_ = channel_messages_endpoint(token, new_channel['channel_id'], 0)

    assert ch_msgs['start'] == 0
    assert ch_msgs['end'] == 50
    assert message_ids[0:50] == [m['message_id'] for m in ch_msgs['messages']]

def test_removal_by_edit_reflected(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    msg = create_message_endpoint(token, new_channel['channel_id'], 'you are a toy')[0]['message_id']
    
    ch_msgs,_ = channel_messages_endpoint(token, new_channel['channel_id'], 0)
    assert ch_msgs['start'] == 0
    assert ch_msgs['end'] == -1
    assert msg in [m['message_id'] for m in ch_msgs['messages']]

'''
Input Error
'''
#channel_id does not refer to a valid channel
def test_invalid_channel_endppoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    _ = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,4,"Howdy Partner!")
    assert status_code == 400

#length of message is less than 1 or over 1000 characters
def test_invalid_short_message_length_endppoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,new_channel['channel_id'],"")
    assert status_code == 400

long_msg = "l"
for i in range(1010):
    long_msg = long_msg + "o"
long_msg = long_msg + "ng"

def test_invalid_long_message_length_endppoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,new_channel['channel_id'],long_msg)
    assert status_code == 400

'''
Access Error
'''

#channel_id is valid and the authorised user is not a member of the channel
def test_invalid_priv_chan_length_endppoint(priv_chan_endpoint):
    token, name, is_public = priv_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    result = register_valid_user(email="jake@gmail.com")
    _,status_code = create_message_endpoint(result['token'],new_channel['channel_id'],"Howdy")
    assert status_code == 403

def test_invalid_pub_chan_length_endppoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    result = register_valid_user(email="jake@gmail.com")
    _,status_code = create_message_endpoint(result['token'],new_channel['channel_id'],"Howdy")
    assert status_code == 403

#invalid token
def test_invalid_token_send_message_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint("token",new_channel['channel_id'],"Howdy Partner!")
    assert status_code == 403