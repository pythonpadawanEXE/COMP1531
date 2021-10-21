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
        response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : new_channel['channel_id'],
        'message' : Message
        })
        message_ids.append(response.json()['message_id'])
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

def remove_message_endpoint(token,message_id):
    response = requests.delete(f"{BASE_URL}/message/remove/v1",json={
        'token' : token,
        'message_id' : message_id,
    })
    return response.json(),response.status_code

'''
Valid Input
'''

def test_channel_valid_message_delete_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code =   remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}

def test_dm_valid_message_delete_endpoint():
    pass

#Custom Input Error?
#If the new message is an empty string, the message is deleted.
def test_channel_double_delete_message_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code = remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}
    #test message is deleted
    _,status_code =  remove_message_endpoint(token,message_ids[0])
    assert status_code == 400

def test_dm__double_delete_message_endpoint():
    pass



'''
Input Error
'''


#message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_channel_invalid_delete_message_id_endpoint(create_messages_endpoint):
    _,token,_ =   create_messages_endpoint
    _,status_code = remove_message_endpoint(token,10)
    assert status_code == 400

def test_dm_invalid_delete_message_id_endpoint():
    pass

'''
Access Error
'''
#editor is not an owner of channel or DM and not the maker of the message
def test_channel_unauthorised_delete_message_id_endpoint(create_messages_endpoint):
    _,_,message_ids =   create_messages_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    _,status_code =   remove_message_endpoint(data['token'],message_ids[0])
    assert status_code == 403

def test_dm_unauthorised_delete_message_id_endpoint():
    pass
