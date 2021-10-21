from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from src.other import decode_jwt



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

#create dm between 2 people
@pytest.fixture
def create_dm_2():
    response_data1 = register_valid_user()
    response_data2 = register_valid_user(email='valid@gmail.com')
    u_ids = [decode_jwt(response_data2)['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : response_data1['token'],
        'u_ids' : u_ids
    })
    return response.json(),response.status_code,response_data1['token'],response_data2['token']


@pytest.fixture
def create_dm_3():
    response_data1 = register_valid_user()
    response_data2 = register_valid_user(email='valid@gmail.com')
    response_data3 = register_valid_user(email='valid1@gmail.com')
    u_ids = [decode_jwt(response_data2)['auth_user_id'],decode_jwt(response_data3)['auth_user_id']]
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : response_data1['token'],
        'u_ids' : u_ids
    })
    return response.json(),response.status_code,response_data1['token'],response_data2['token']

def send_msg(token,dm_id,message):
    response = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : dm_id,
        'message' : message
        })
    return response.json(),response.status_code

#create multiple messages in a dm 


'''
Valid Message
'''

def test_send_dms_2_endpoint_dm_maker(create_dm_2):
    dm_data, status_code,token,_ = create_dm_2
    assert status_code == 200

    
    for i in range(5):
        Message = "message" + str(i)
        _ , status_code =  send_msg(token,dm_data['dm_id'],Message)
        message_ids.append(response.json()['message_id'])
        assert status_code == 200
    
def test_send_dms_3_endpoint_dm_maker(create_dm_3):
    dm_data, status_code,_,token = create_dm_3
    assert status_code == 200

    for i in range(5):
        Message = "message" + str(i)
        msg_data , status_code =  send_msg(token,dm_data['dm_id'],Message)
        assert status_code == 200

'''
Input Error
'''
def test_invalid_dm_id(create_dm_3):
        dm_data, status_code,_,token = create_dm_3
    assert status_code == 200

    for i in range(5):
        Message = "message" + str(i)
        msg_data , status_code =  send_msg(token,10,Message)
        assert status_code == 400

def test_invalid_long_msg_(create_dm_3):
        dm_data, status_code,_,token = create_dm_3
    assert status_code == 200
    long_msg = "l"
    for i in range(1010):
        long_msg = long_msg + "o"
    long_msg = long_msg + "ng"
    msg_data , status_code =  send_msg(token,10,long_msg)
    assert status_code == 400

'''
Access Error
'''
def test_send_dms_3_endpoint_unauthorised(create_dm_3):
    dm_data, status_code,_,token = create_dm_3
    assert status_code == 200
    response_data = register_valid_user(email='unauthorised@gmail.com')
    for i in range(5):
        Message = "message" + str(i)
        msg_data , status_code =  send_msg(response_data['token'],dm_data['dm_id'],Message)
        assert status_code == 200



        
