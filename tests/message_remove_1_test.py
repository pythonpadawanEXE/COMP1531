from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from tests.helper_test_funcs import register_valid_user,channel_messages_endpoint,\
    create_channel_endpoint,create_message_endpoint,remove_message_endpoint,send_msg,\
        message_send_endpoint


BASE_URL = config.url

'''
Valid Input
'''
def test_owner_global_owner_original_poster_can_remove_members_message():
    response_data = register_valid_user(email='first@gmail.com')
    msg_text = "hello, world"
    
    
    user = register_valid_user(email='valid1@gmail.com')
    user2 = register_valid_user(email='valid2@gmail.com')

    new_channel = create_channel_endpoint(user['token'],'name',True)

    _ = requests.post(config.url + 'channel/join/v2', json={'token':user2['token'], 'channel_id': new_channel['channel_id']})

    msg0 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text)
    msg1 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"2")
    

    remove_message_endpoint(response_data['token'], msg0['message_id'])
    ch_msgs,_ = channel_messages_endpoint(response_data['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg1['message_id']

    msg2 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"3")
    remove_message_endpoint(user['token'], msg1['message_id'])
    ch_msgs,_ = channel_messages_endpoint(response_data['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg2['message_id']

    msg3 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"4")
    remove_message_endpoint(user2['token'], msg2['message_id'])
    ch_msgs,_ = channel_messages_endpoint(user2['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg3['message_id']


def test_channel_valid_message_delete_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code =   remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}

def test_dm_valid_message_delete_endpoint(create_dms_endpoint):
    _,token,message_ids =   create_dms_endpoint
    data,status_code =   remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}


#If the new message is an empty string, the message is deleted.
def test_channel_double_delete_message_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code = remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}
    #test message is deleted
    _,status_code =  remove_message_endpoint(token,message_ids[0])
    assert status_code == 400
    
def test_dm_double_delete_message_endpoint(create_dms_endpoint):
    _,token,message_ids =   create_dms_endpoint
    data,status_code = remove_message_endpoint(token,message_ids[0])
    assert status_code == 200
    assert data == {}
    #test message is deleted
    _,status_code =  remove_message_endpoint(token,message_ids[0])
    assert status_code == 400

'''
Input Error
'''
#message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_channel_invalid_delete_message_id_endpoint(create_messages_endpoint):
    _,token,_ =   create_messages_endpoint
    _,status_code = remove_message_endpoint(token,10)
    assert status_code == 400

def test_dm_invalid_delete_message_id_endpoint(create_dms_endpoint):
    _,token,_ =   create_dms_endpoint
    _,status_code = remove_message_endpoint(token,10)
    assert status_code == 400

'''
Access Error
'''
#editor is not an owner of channel or DM and not the maker of the message
def test_channel_unauthorised_delete_message_id_endpoint(create_messages_endpoint):
    _,_,message_ids =   create_messages_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    _,status_code =   remove_message_endpoint(data['token'],message_ids[0])
    assert status_code == 403

def test_dm_unauthorised_delete_message_id_endpoint(create_dms_endpoint):
    _,_,message_ids =   create_dms_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    _,status_code =   remove_message_endpoint(data['token'],message_ids[0])
    assert status_code == 403
