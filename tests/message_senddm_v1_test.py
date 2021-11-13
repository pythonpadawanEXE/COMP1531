from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from src.other import decode_jwt
from tests.helper_test_funcs import send_msg,register_valid_user


BASE_URL = config.url




'''
Valid Message
'''

def test_send_dms_2_endpoint_dm_maker(create_dm_2):
    dm_data, status_code,token,_ = create_dm_2
    assert status_code == 200

    
    for i in range(5):
        Message = "message" + str(i)
        _ , status_code =  send_msg(token,dm_data['dm_id'],Message)
        assert status_code == 200
    
def test_send_dms_3_endpoint_dm_maker(create_dm_3):
    dm_data, status_code,_,token = create_dm_3
    assert status_code == 200

    for i in range(5):
        Message = "message" + str(i)
        _ , status_code =  send_msg(token,dm_data['dm_id'],Message)
        assert status_code == 200

'''
Input Error
'''
def test_invalid_dm_id(create_dm_3):
    _, status_code,_,token = create_dm_3
    assert status_code == 200

    for i in range(5):
        Message = "message" + str(i)
        _ , status_code =  send_msg(token,10,Message)
        assert status_code == 400

def test_invalid_dm_long_msg_(create_dm_3):
    _, status_code,_,token = create_dm_3
    assert status_code == 200
    long_msg = "l"
    for _ in range(1010):
        long_msg = long_msg + "o"
    long_msg = long_msg + "ng"
    _ , status_code =  send_msg(token,10,long_msg)
    assert status_code == 400

def test_invalid_dm_short_msg_(create_dm_3):
    _, status_code,_,token = create_dm_3
    assert status_code == 200
    
    _ , status_code =  send_msg(token,10,"")
    assert status_code == 400

'''
Access Error
'''
def test_send_dms_3_endpoint_unauthorised(create_dm_3):
    dm_data, status_code,_,_ = create_dm_3
    assert status_code == 200
    response_data = register_valid_user(email='unauthorised@gmail.com')
    for i in range(5):
        Message = "message" + str(i)
        _ , status_code =  send_msg(response_data['token'],dm_data['dm_id'],Message)
        assert status_code == 403



        
