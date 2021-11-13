from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from tests.helper_test_funcs import register_valid_user,channel_messages_endpoint,\
    create_channel_endpoint,message_send_endpoint

BASE_URL = config.url

"""
Valid Input
"""

#start is not greater than the total number of messages in the channel
def test_valid_start_index_0_endpoint(create_messages_endpoint):
    new_channel,token,_ = create_messages_endpoint
    print(f"new_channel var {new_channel}")
    result,status_code = channel_messages_endpoint(token,new_channel['channel_id'],1)
    assert status_code == 200
    assert result["end"] == -1


def test_valid_message():
    msg_text = "hello, world"
    user = register_valid_user()
    channel = create_channel_endpoint(user['token'],'Channel',True)
    msg = message_send_endpoint(user['token'],channel['channel_id'], msg_text)
    
    ch_msgs,_ = channel_messages_endpoint(user['token'],channel['channel_id'], 0)
    
    assert ch_msgs['messages'][0]['message_id'] == msg['message_id']

def test_valid_start_index_1_endpoint(create_messages_endpoint):
    new_channel,token,_ = create_messages_endpoint
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
    new_channel,token,_ = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],4)
    assert status_code == 200

"""
Input Errors
"""

#start is not less than 0
def test_invalid_negative_start_index_endpoint(create_messages_endpoint):
    new_channel,token,_ = create_messages_endpoint
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
    new_channel,token,_ = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],50)
    assert status_code == 400

def test_invalid_start_index_5_endpoint(create_messages_endpoint):
    new_channel,token,_ = create_messages_endpoint
    _,status_code = channel_messages_endpoint(token,new_channel['channel_id'],5)
    response = requests.get(f"{BASE_URL}/get_data")
    print(response.json())
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
