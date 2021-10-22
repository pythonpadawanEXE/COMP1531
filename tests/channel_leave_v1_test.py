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

def channel_leave(token, channel_id):

    '''
    Removes a user with token to channel with ID channel_id
    '''

    response = requests.post(f"{BASE_URL}channel/leave/v1", json={
        'token' : token,
        'channel_id' : channel_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Public channel with one user who leaves, user is also owner
def test_individual_public():
    # Create a user1
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    user1_token = user1['token']
    user1_uid = user1['auth_user_id']

    # Create a user2
    user2 = register_user("jemma@email.com", "1234578sR", "Jemma", "Smith")
    user2_token = user2['token']
    
    # User creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    # User 2 join channel
    channel_join(user2_token, channel_id)

    # User leaves the channel
    channel_leave(user1_token, channel_id)

    # Check if user isnt in channel using channel details
    details = channel_details(user2_token, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(user1_uid != user['u_id'])

    # Loop through the channel details and find if auth_user_id is not in owner_members
    for user in details['owner_members']:
        assert(user1_uid != user['u_id'])

# Public channel with 2 users, normal channel member leaves
def test_multiple_users():
    # Create a user1
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    user1_token = user1['token']

    # Create a user2
    user2 = register_user("jemma@email.com", "123456789sR", "Jemma", "Smith")
    user2_token = user2['token']
    user2_uid = user2['auth_user_id']
    
    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    # User2 joins channel 
    channel_join(user2_token, channel_id)

    # User2 leaves the channel
    channel_leave(user2_token, channel_id)

    # Get the channel details
    details = channel_details(user1_token, channel_id)

    # Loop through the channel details and find if user2_uid is not in all_members
    for user in details['all_members']:
        assert(user2_uid != user['u_id'])

# Public channel with 2 users, owner user leaves
def test_multiple_users_owner():
    # Create a user1
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    user1_token = user1['token']
    user1_uid = user1['auth_user_id']

    # Create a user2
    user2 = register_user("jemma@email.com", "123456789sR", "Jemma", "Smith")
    user2_token = user2['token']
    
    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    # User2 joins channel 
    channel_join(user2_token, channel_id)

    # User1 leaves the channel
    channel_leave(user1_token, channel_id)

    # Get the channel details
    details = channel_details(user2_token, channel_id)

    # Loop through the channel details and find if user1_uid is not in all_members
    for user in details['all_members']:
        assert(user1_uid != user['u_id'])

    # Loop through the channel details and find if user1_uid is not in owner_members
    for user in details['owner_members']:
        assert(user1_uid != user['u_id'])

# Public channel with 2 users, owner and normal member leaves
def test_multiple_users_all():
    # Create a user1
    user1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    user1_token = user1['token']
    user1_uid = user1['auth_user_id']

    # Create a user2
    user2 = register_user("jemma@email.com", "123456789sR", "Jemma", "Smith")
    user2_token = user2['token']
    user2_uid = user2['auth_user_id']

    # Create a user3
    user3 = register_user("jasoon@email.com", "123489sR", "Jason", "Smith")
    user3_token = user3['token']
    
    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    # User2 joins channel 
    channel_join(user2_token, channel_id)
    # User3 joins channel 
    channel_join(user3_token, channel_id)

    # User1 leaves the channel
    channel_leave(user1_token, channel_id)
    # User2 leaves the channel
    channel_leave(user2_token, channel_id)

    # Get the channel details
    details = channel_details(user3_token, channel_id)

    # Loop through the channel details and find if both users is not in all_members
    for user in details['all_members']:
        assert(user1_uid != user['u_id'])
        assert(user2_uid != user['u_id'])

    # Loop through the channel details and find if both users is not in owner_members
    for user in details['owner_members']:
        assert(user1_uid != user['u_id'])
        assert(user2_uid != user['u_id'])

# Channel ID given is not valid
def test_invalid_channel():
    response = requests.post(f"{BASE_URL}channel/leave/v1", json={
        'token' : register_user("js@email.com", "ABCDEFGH", "John", "Smith")['token'],
        'channel_id' : 9999,
    })
    assert response.status_code == 400

# User is not a member of given valid channel ID
def test_invalid_user():
    # Create User1
    user1_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['token']

    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    response = requests.post(f"{BASE_URL}channel/leave/v1", json={
        'token' : "9999",
        'channel_id' : channel_id,
    })
    assert response.status_code == 403

# channel_id is valid and the authorised user is not a member of the channel
def test_invalid_auth_user_id():
    # Create User1
    user1_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['token']
    user2_token = register_user("jemma@email.com", "ABCDEFGH", "jemma", "Smith")['token']

    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    response = requests.post(f"{BASE_URL}channel/leave/v1", json={
        'token' : user2_token,
        'channel_id' : channel_id,
    })
    assert response.status_code == 403

# channel_id is valid and the authorised user is not a member of the channel
def test_invalid_token():
    # Create User1
    user1_token = register_user("js@email.com", "ABCDEFGH", "John", "Smith")['token']

    # User1 creates a public channel
    channel_id = channels_create(user1_token, "Chan 1", True)['channel_id']

    response = requests.post(f"{BASE_URL}channel/leave/v1", json={
        'token' : "ByJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoX3VzZXJfaWQiOjEsInNlc3Npb25faWQiOjJ9.Env14G_7NFpwl6w_pDX4SPknTJelqy8GgdcaA44rrmM",
        'channel_id' : channel_id,
    })
    assert response.status_code == 403