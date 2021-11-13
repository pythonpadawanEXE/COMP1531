from requests.models import Response
from src import auth,config,other
import re
import pytest
from src.data_store import data_store
from src.error import InputError
import requests
from tests.helper_test_funcs import  register_valid_user,create_channel_endpoint,\
    send_msg

BASE_URL = config.url

@pytest.fixture(scope='function',autouse=True)
def clear_all():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

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

@pytest.fixture
def create_dms_endpoint(create_dm_3):
    dm_data, status_code,_,token = create_dm_3
    assert status_code == 200
    message_ids = []
    for i in range(5):
        Message = "message" + str(i)
        response_data , status_code =  send_msg(token,dm_data['dm_id'],Message)
        assert status_code == 200
        message_ids.append(response_data['message_id'])
    return dm_data['dm_id'],token,message_ids

@pytest.fixture
def create_dm_3():
    response_data1 = register_valid_user()
    response_data2 = register_valid_user(email='valid@gmail.com')
    response_data3 = register_valid_user(email='valid1@gmail.com')
    u_ids = [response_data2['auth_user_id'],response_data3['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : response_data1['token'],
        'u_ids' : u_ids
    })
    return response.json(),response.status_code,response_data1['token'],response_data2['token']

    #create dm between 2 people

@pytest.fixture
def create_dm_2():
    response_data1 = register_valid_user()
    response_data2 = register_valid_user(email='valid@gmail.com')
    u_ids = [response_data2['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : response_data1['token'],
        'u_ids' : u_ids
    })
    return response.json(),response.status_code,response_data1['token'],response_data2['token']