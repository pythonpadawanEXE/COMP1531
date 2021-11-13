from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from tests.helper_test_funcs import  register_valid_user,get_profile,channel_messages_endpoint,\
    create_channel_endpoint,create_message_endpoint


BASE_URL = config.url


'''
Valid Input
'''
#Valid Message
def test_valid_send_message_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,new_channel['channel_id'],"Howdy Partner!")
    assert status_code == 200

def test_valid_tag_send_message_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    register_valid_user(email="jake@gmail.com",password="1234567",name_first="jake")
    new_channel = create_channel_endpoint(token,name,is_public)
    _,status_code = create_message_endpoint(token,new_channel['channel_id'],"Howdy Partner @haydeneverest @jakeeverest !")
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