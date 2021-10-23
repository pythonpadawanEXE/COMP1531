# user_profile_setemail_v1_test.py
# pytest file to test the implementation of user_profile_setemail_v1

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

def update_email(token, email):

    '''
    Update the authorised user's email
    '''

    response = requests.put(f"{BASE_URL}user/profile/setemail/v1", json={
        'token' : token,
        'email' : email
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Update the authorised user's email address
def test_update_user_email():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']
    auth_user_id = user['auth_user_id']

    # Update users email
    update_email(token, "johnsmith@gmail.com")

    # Check if users name has been changed
    user_details = user_profile_details(token, auth_user_id)
    assert(user_details['email'] == "johnsmith@gmail.com")

# email entered is not a valid email
def test_email_invalid():
    # New user
    user = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token = user['token']

    # Update users email
    response = requests.put(f"{BASE_URL}user/profile/setemail/v1", json={
        'token' : token,
        'email' : "ankitrai326.com"
    })

    assert response.status_code == 400

# email address is already being used by another user
def test_email_in_use():
    # New user
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    user2 = register_user("jemma@email.com", "ABCDEFGH", "Jemma", "Smith")
    token = user1['token']

    # Update users email to user2 email
    response = requests.put(f"{BASE_URL}user/profile/setemail/v1", json={
        'token' : token,
        'email' : "jemma@email.com"
    })

    assert response.status_code == 400