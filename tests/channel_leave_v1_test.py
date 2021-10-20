# channel_leave_v1_test.py
# pytest file to test the implementation of channel_leave_v1 endpoint

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

# Public channel with one user who leaves, user is also global owner
def test_individual_public():
    pass

# Private channel with one user who leaves, user is also global owner
def test_individual_private():
    pass

# Public channel with 2 users, normal channel member leaves
def test_multiple_users():
    pass

# Public channel with 2 users, global owner user leaves
def test_multiple_users_owner():
    pass

# Public channel with 2 users, global owner and normal member leaves
def test_multiple_users_all():
    pass

# Channel ID given is not valid for that user
def test_invalid_channel():
    pass

# User is not a member of given valid channel ID
def test_invalid_user():
    pass