# channel_addowner_v1_test.py
# pytest file to test the implementation of channel_addowner_v1 endpoint

import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(f"{BASE_URL}clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users uid and token
    '''

    response = requests.post(f"{BASE_URL}auth/register/v2",json={
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

def channels_create(token, name, is_public):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.post(f"{BASE_URL}channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_join(token, channel_id):

    '''
    Adds a user with token to channel with ID channel_id
    '''

    response = requests.post(f"{BASE_URL}channel/join/v2", json={
        'token' : token,
        'channel_id' : channel_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_details(token, channel_id):

    '''
    Creates a channel for user with given token and returns the channel ID
    '''

    response = requests.get(f"{BASE_URL}channel/details/v2?token={token}&channel_id={channel_id}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Make user with user id u_id an owner of the channel
def make_u_id_channel_owner():
    pass

# channel_id does not refer to a valid channel
def test_invalid_channel_id():
    pass

# u_id does not refer to a valid user
def test_invalid_u_id():
    pass

# u_id refers to a user who is not a member of the channel
def test_u_id_not_member_channel():
    pass

# u_id refers to a user who is already an owner of the channel
def test_u_id_already_owner():
    pass

# channel_id is valid and the authorised user (token) does not have owner permissions in the channel
def test_token_is_not_channel_owner():
    pass
