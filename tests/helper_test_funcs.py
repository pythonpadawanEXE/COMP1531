from src import auth,config,other
import re
import pytest
from src.data_store import data_store
from src.error import InputError,AccessError
import requests
from src.other import decode_jwt


BASE_URL = config.url


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

def get_profile(token,u_id):   
    response = requests.get(f"{BASE_URL}/user/profile/v1",params={
        'token' : token,
        'u_id' : u_id
    }) 
    assert response.status_code == 200
    return response.json()

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

def message_send_endpoint(token,channel_id,message):
    response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    assert response.status_code == 200 
    return response.json()

def login_valid_user(email = 'validemail@gmail.com',password = '123abc!@#'):
    response = requests.post(f"{BASE_URL}/auth/login/v2",json={
        'email' : email,
        'password' : password
    })
    assert response.status_code == 200
    response_data = response.json()
    print(response_data)
    assert isinstance(response_data['token'],str)
    assert isinstance(response_data['auth_user_id'],int)
    return response_data

def login_invalid_user(email = 'validemail@gmail.com',password = '123abc!@#'):
    response = requests.post(f"{BASE_URL}/auth/login/v2",json={
        'email' : email,
        'password' : password
    })
    assert response.status_code == 400

def logout_invalid_user(token):
    response = requests.post(f"{BASE_URL}/auth/logout/v1",json={
        'token' : token
    })
    assert response.status_code == 403

def token_validity_check_pytest(token,store):
    decoded_token = decode_jwt(token)
    users = store['users']
    for user in users:
        if user['u_id'] == decoded_token['auth_user_id']:
            for session_id in user['sessions']:
                if session_id == decoded_token['session_id']:
                    return {'auth_user_id':decoded_token['auth_user_id'],'session_id':decoded_token['session_id']}
    raise AccessError(description="Invalid Token")

def logout_valid_user(token):
    response = requests.post(f"{BASE_URL}/auth/logout/v1",json={
        'token' : token
    })
    assert response.status_code == 200
    assert response.json() == {}
    store = (requests.get(f"{BASE_URL}/get_data")).json()
    with pytest.raises(AccessError):
        token_validity_check_pytest(token,store)

def create_message_endpoint(token,channel_id,message):
    response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    return response.json(),response.status_code

def edit_message_endpoint(token,message_id,message):
    response = requests.put(f"{BASE_URL}/message/edit/v1",json={
        'token' : token,
        'message_id' : message_id,
        'message' : message
    })
    return response.json(),response.status_code

def message_send_endpoint(token,channel_id,message):
    response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    assert response.status_code == 200 
    return response.json()

def remove_message_endpoint(token,message_id):
    response = requests.delete(f"{BASE_URL}/message/remove/v1",json={
        'token' : token,
        'message_id' : message_id,
    })
    return response.json(),response.status_code

def send_msg(token,dm_id,message):
    response = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : dm_id,
        'message' : message
        })
    return response.json(),response.status_code
