# user_profile_setname_v1_test.py
# pytest file to test the implementation of user_profile_setname_v1

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

def user_profile_details(token, u_id):

    '''
    For a valid user, returns information about their user_id, email, first name, last name, and handle
    '''

    response = requests.get(f"{BASE_URL}user/profile/v1?token={token}&u_id={u_id}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def update_name(token, name_first, name_last):

    '''
    Update the authorised user's first and last name
    '''

    response = requests.put(f"{BASE_URL}user/profile/setname/v1", json={
        'token' : token,
        'name_first' : name_first,
        'name_last' : name_last
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Update the authorised user's first and last name
def update_user_first_last_name():
    pass

# length of name_first is not between 1 and 50 characters inclusive
def name_first_invalid_length():
    pass

# length of name_last is not between 1 and 50 characters inclusive
def name_last_invalid_length():
    pass