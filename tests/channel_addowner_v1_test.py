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

def channel_addowner(token, channel_id, u_id):
    '''
    Makes u_id a channel owner of channel with ID channel_id
    '''

    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token,
        'channel_id' : channel_id,
        'u_id' : u_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Make user with user with id u_id an owner of the channel
def test_make_u_id_channel_owner():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']
    auth_user_id_2 = user_2['auth_user_id']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user1 promotes user2 as channel owner
    channel_addowner(token_1, channel_id, auth_user_id_2)

    # get channel details
    details = channel_details(token_1, channel_id)

    # check if user2 is an owner of channel_id
    assert(details['owner_members'][1]['u_id'] == auth_user_id_2)

# channel_id does not refer to a valid channel
def test_invalid_channel_id():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']
    auth_user_id_2 = user_2['auth_user_id']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user1 promotes user2 as channel owner with invalid channel_id
    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token_1,
        'channel_id' : 9999,
        'u_id' : auth_user_id_2,
    })
    assert response.status_code == 400

# u_id does not refer to a valid user
def test_invalid_u_id():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user1 promotes user2 as channel owner with invalid channel_id
    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token_1,
        'channel_id' : channel_id,
        'u_id' : 35,
    })
    assert response.status_code == 400

# u_id refers to a user who is not a member of the channel
def test_u_id_not_member_channel():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']

    # Create user3
    user_3 = register_user("mike@email.com", "ABCDEFGH", "Mike", "Smith")
    auth_user_id_3 = user_3['auth_user_id']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user1 promotes user3 as channel owner
    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token_1,
        'channel_id' : channel_id,
        'u_id' : auth_user_id_3,
    })
    assert response.status_code == 400

# u_id refers to a user who is already an owner of the channel
def test_u_id_already_owner():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']
    auth_user_id_2 = user_2['auth_user_id']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user1 promotes user2 as channel owner
    channel_addowner(token_1, channel_id, auth_user_id_2)

    # get channel details
    details = channel_details(token_1, channel_id)

    # check if user2 is an owner of channel_id
    assert(details['owner_members'][1]['u_id'] == auth_user_id_2)

    # user1 promotes user2 as channel owner again
    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token_1,
        'channel_id' : channel_id,
        'u_id' : auth_user_id_2,
    })
    assert response.status_code == 400

# channel_id is valid and the authorised user (token) does not have owner permissions in the channel
def test_token_is_not_channel_owner():
    # Create user1
    user_1 = register_user("js@email.com", "ABCDEFGH", "John", "Smith")
    token_1 = user_1['token']

    # Create user2
    user_2 = register_user("jems@email.com", "ABCDEFGH", "Jemma", "Smith")
    token_2 = user_2['token']

    # Create user3
    user_3 = register_user("mike@email.com", "ABCDEFGH", "Mike", "Smith")
    auth_user_id_3 = user_3['auth_user_id']
    token_3 = user_3['token']

    # user1 creates a channel
    channel_id = channels_create(token_1, "Chan 1", True)['channel_id']

    # user2 joins user1's channel
    channel_join(token_2, channel_id)

    # user3 joins user1's channel
    channel_join(token_3, channel_id)

    # user2 promotes user1 as channel owner again
    response = requests.post(f"{BASE_URL}channel/addowner/v1", json={
        'token' : token_2,
        'channel_id' : channel_id,
        'u_id' : auth_user_id_3,
    })
    assert response.status_code == 403
