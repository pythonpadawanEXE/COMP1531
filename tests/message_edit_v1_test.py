from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from tests.helper_test_funcs import register_valid_user,channel_messages_endpoint,\
    create_channel_endpoint, edit_message_endpoint,message_send_endpoint,send_msg,remove_message_endpoint

BASE_URL = config.url

'''
Valid Input
'''
def test_owner_global_owner_original_poster_can_edit_members_channel_message():
    response_data = register_valid_user(email='first@gmail.com')
    msg_text = "hello, world"
    
    
    user = register_valid_user(email='valid1@gmail.com')
    user2 = register_valid_user(email='valid2@gmail.com')

    new_channel = create_channel_endpoint(user['token'],'name',True)

    _ = requests.post(config.url + 'channel/join/v2', json={'token':user2['token'], 'channel_id': new_channel['channel_id']})

    msg0 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text)
    msg1 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"2")
    

    edit_message_endpoint(response_data['token'], msg0['message_id'],"hello_world0")
    ch_msgs,_ = channel_messages_endpoint(response_data['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg1['message_id']

    msg2 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"3")
    edit_message_endpoint(user['token'], msg1['message_id'],"hello_world1")
    ch_msgs,_ = channel_messages_endpoint(response_data['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg2['message_id']

    msg3 = message_send_endpoint(user['token'],new_channel['channel_id'], msg_text+"4")
    edit_message_endpoint(user2['token'], msg2['message_id'],"hello_world2")
    ch_msgs,_ = channel_messages_endpoint(user2['token'], new_channel['channel_id'],0)
    assert ch_msgs['messages'][0]['message_id'] == msg3['message_id']

def test_channel_valid_message_edit_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code = edit_message_endpoint(token,message_ids[0],"Modified message.")
    assert status_code == 200
    assert data == {}

def test_valid_tag_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    register_valid_user(email="jake@gmail.com",password="1234567",name_first="jake")
    data,status_code = edit_message_endpoint(token,message_ids[0],"Modified message @haydeneverest @jakeeverest .")
    assert status_code == 200
    assert data == {}

def test_dm_valid_message_edit_endpoint(create_dms_endpoint):
    _, token,message_ids = create_dms_endpoint
    data,status_code = edit_message_endpoint(token,message_ids[0],"Modified message.")
    assert status_code == 200
    assert data == {}

def test_dm_owner_edit_message_id_endpoint():
    response_data1 = register_valid_user()
    response_data2 = register_valid_user(email='valid@gmail.com')
    response_data3 = register_valid_user(email='valid1@gmail.com')
    u_ids = [response_data2['auth_user_id'],response_data3['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : response_data1['token'],
        'u_ids' : u_ids
    })
    message_ids = []
    dm_data = response.json()
    for i in range(5):
        Message = "message" + str(i)
        response_data , status_code =  send_msg(response_data1['token'],dm_data['dm_id'],Message)
        assert status_code == 200
        message_ids.append(response_data['message_id'])
    _,status_code =   edit_message_endpoint(response_data1['token'],message_ids[0],"NEw Msg")
    assert status_code == 200


#If the new message is an empty string, the message is deleted.
def test_channel_delete_short_message_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    data,status_code =   edit_message_endpoint(token,message_ids[0],"")
    assert status_code == 200
    assert data == {}
    #test message is deleted
    data,status_code = edit_message_endpoint(token,message_ids[0],"yes")
    assert status_code == 400

def test_dm_delete_short_message_endpoint(create_dms_endpoint):
    _,token,message_ids =   create_dms_endpoint
    data,status_code =   edit_message_endpoint(token,message_ids[0],"")
    assert status_code == 200
    assert data == {}
    #test message is deleted
    data,status_code = edit_message_endpoint(token,message_ids[0],"yes")
    assert status_code == 400    



'''
Input Error
'''
long_msg = "l"
for i in range(1010):
    long_msg = long_msg + "o"
long_msg = long_msg + "ng"
#length of message is over 1000 characters
def test_channel_invalid_long_message_endpoint(create_messages_endpoint):
    _,token,message_ids =   create_messages_endpoint
    _,status_code =   edit_message_endpoint(token,message_ids[0],long_msg)
    assert status_code == 400

def test_dm_invalid_long_message_endpoint(create_dms_endpoint):
    _,token,message_ids =   create_dms_endpoint
    _,status_code =   edit_message_endpoint(token,message_ids[0],long_msg)
    assert status_code == 400

#message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_channel_invalid_message_id_endpoint(create_messages_endpoint):
    _,token,_ = create_messages_endpoint
    _,status_code = edit_message_endpoint(token,10,"NEw Msg")
    assert status_code == 400

def test_channel_already_deleted_endpoint(create_messages_endpoint):
    _,token,_ = create_messages_endpoint
    _ ,status_code =  remove_message_endpoint(token,0)
    assert status_code == 200
    _,status_code = edit_message_endpoint(token,0,"NEw Msg")
    assert status_code == 400
    # assert 1 == 0

def test_dm_invalid_edit_message_id_endpoint(create_dms_endpoint):
    _,token,_ = create_dms_endpoint
    _,status_code = edit_message_endpoint(token,10,"NEw Msg")
    assert status_code == 400

    
'''
Access Error
'''
#editor is not an owner of channel or DM and not the maker of the message
def test_channel_unauthorised_edit_message_id_endpoint(create_messages_endpoint):
    _,_,message_ids =   create_messages_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    _,status_code =   edit_message_endpoint(data['token'],message_ids[0],"NEw Msg")
    assert status_code == 403

def test_dm_unauthorised_edit_message_id_endpoint(create_dms_endpoint):
    _,_,message_ids =   create_dms_endpoint
    data = register_valid_user(email = "newemail@gmail.com")
    _,status_code =   edit_message_endpoint(data['token'],message_ids[0],"NEw Msg")
    assert status_code == 403


