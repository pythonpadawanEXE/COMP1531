# user_profile_sethandle_v1_test.py
# pytest file to test the implementation of user_profile_sethandle_v1

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

def update_handle(token, handle_str):

    '''
    Update the authorised user's handle (i.e. display name)
    '''

    response = requests.put(f"{BASE_URL}user/profile/sethandle/v1", json={
        'token' : token,
        'handle_str' : handle_str
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Update the authorised user's handle
def test_update_user_handle():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']
    auth_user_id = user['auth_user_id']

    # Update users handle
    update_handle(token, "JohnSmith1997")

    # Check if users handle has been changed
    user_details = user_profile_details(token, auth_user_id)
    assert(user_details['handle_str'] == "JohnSmith1997")

# length of handle_str is not between 3 and 20 characters inclusive    
def test_handle_length_invalid():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']

    # Update users handle
    response = requests.put(f"{BASE_URL}user/profile/sethandle/v1", json={
        'token' : token,
        'handle_str' : "HI"
    })

    assert response.status_code == 400

# handle_str contains characters that are not alphanumeric
# a-z, A-Z, 0-9
def test_handle_non_alphanumeric():
    # New user
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user1['token']

    # Update users handle
    response = requests.put(f"{BASE_URL}user/profile/sethandle/v1", json={
        'token' : token,
        'handle_str' : "John$mith"
    })

    assert response.status_code == 400

# the handle is already used by another user
def test_handle_in_use():
    # New user
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user1['token']

    # Create 2nd user
    register_user("jemma@email.com", "ABCDEdsFGH", "Jemma", "Smith")

    # Update users handle to 2nd users handle
    response = requests.put(f"{BASE_URL}user/profile/sethandle/v1", json={
        'token' : token,
        'handle_str' : "jemmasmith"
    })

    assert response.status_code == 400