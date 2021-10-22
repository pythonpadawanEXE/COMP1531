import pytest
import requests
from requests.models import Response
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

def dm_create(token, u_ids):

    '''
    Creates a dm for user with given token and other's u_ids returns the dm ID
    '''

    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : token,
        'u_ids' : u_ids,
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_details(token, dm_id):

    response = requests.get(f"{BASE_URL}dm/details/v1?token={token}&dm_id={dm_id}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_leave(token, dm_id):

    '''
    Removes a user with token to dm with dm_id
    '''

    response = requests.post(f"{BASE_URL}dm/leave/v1", json={
        'token' : token,
        'dm_id' : dm_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data
    
def test_dm_member_leave():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_token = member['token']
    member_u_ids = [member['auth_user_id']]
    # Dm ID
    dm_id = dm_create(creator_token, member_u_ids)['dm_id']
    # Dm details before member leave
    details_before = dm_details(creator_token, dm_id)
    # User_ids in dm before member leave
    auth_user_id_list = [creator['auth_user_id'], member['auth_user_id']]
    # Loop through the dm details and find if auth_user_ids are in all_members
    for user in details_before['all_members']:
        assert(user['u_id'] in auth_user_id_list)
    
    #member leave
    dm_leave(member_token, dm_id)
    #Dm details after member leave
    details_after = dm_details(creator_token, dm_id)
    # Loop through the dm details and find if removed member is still in all_members of dm
    for user in details_after['all_members']:
        assert(member['auth_user_id'] != user['u_id'] )
    # As the creator leaves, calling the dm/detail_v1 function would raise AccessError
    response = requests.get(f"{BASE_URL}dm/details/v1?token={member_token}&dm_id={dm_id}")
    assert response.status_code == 403

def test_dm_owner_leave():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_token = member['token']
    member_u_ids = [member['auth_user_id']]
    # Dm ID
    dm_id = dm_create(creator_token, member_u_ids)['dm_id']
    # Dm details before owner leave
    details_before = dm_details(creator_token, dm_id)
    # User_ids in dm before owner leave
    auth_user_id_list = [creator['auth_user_id'], member['auth_user_id']]
    # Loop through the dm details and find if auth_user_id is in all_members
    for user in details_before['all_members']:
        assert(user['u_id'] in auth_user_id_list)
    
    #owner leave
    dm_leave(creator_token, dm_id)
    #Dm details after owner leave
    details_after = dm_details(member_token, dm_id)
    # Loop through the dm details and find if removed creater is still in all_members of dm
    for user in details_after['all_members']:
        assert(creator['auth_user_id'] != user['u_id'])
    # Dm owner should be empty after the owner leave
    assert(details_after['owner'] == [])
    # As the creator leaves, calling the dm/detail_v1 function would raise AccessError
    response = requests.get(f"{BASE_URL}dm/details/v1?token={creator_token}&dm_id={dm_id}")
    assert response.status_code == 403

def test_leave_invalid_dm():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_u_ids = [member['auth_user_id']]
    dm_create(creator_token, member_u_ids)
    #Input error is expected to be raised for a invalid dm
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : creator_token,
        'u_ids' : '999',
    })
    assert response.status_code == 400

def test_leave_member_not_in_dm():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_u_ids = [member['auth_user_id']]
    dm_id = dm_create(creator_token, member_u_ids)
    #Input error is expected to be raised for a invalid dm
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : "",
        'u_ids' : dm_id,
    })
    assert response.status_code == 403