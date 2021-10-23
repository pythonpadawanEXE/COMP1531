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

def test_dm_details():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    token = creator['token']
    u_ids = [member['auth_user_id']]
    # Dm ID
    dm_id = dm_create(token, u_ids)['dm_id']
    # Dm details
    details = dm_details(token, dm_id)
    # User_ids
    auth_user_id_list = [creator['auth_user_id'], member['auth_user_id']]
    # Loop through the dm details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(user['u_id'] in auth_user_id_list)

def test_bad_token():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    token = creator['token']
    u_ids = [member['auth_user_id']]
    # Dm ID
    dm_id = dm_create(token, u_ids)['dm_id']
    # Dm details
    details = requests.get(f"{BASE_URL}dm/details/v1?token={''}&dm_id={dm_id}")
    assert details.status_code == 403

def test_invalid_dm_id():
    # New dm
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    token = creator['token']
    u_ids = [member['auth_user_id']]
    dm_create(token, u_ids)
    details = requests.get(f"{BASE_URL}dm/details/v1?token={token}&dm_id={999}")
    assert details.status_code == 400

def test_unauthoried_user():
    # New dm
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    unauthoried_user = register_user("he@email.com", "he123!@#", "Hayden", "Everest")
    creator_token = creator['token']
    unauthoried_user_token = unauthoried_user['token']
    u_ids = [member['auth_user_id']]
    dm_id = dm_create(creator_token, u_ids)['dm_id']
    details = requests.get(f"{BASE_URL}dm/details/v1?token={unauthoried_user_token}&dm_id={dm_id}")
    assert details.status_code == 403

def test_multi_dm_details():
    # New users
    creator1 = register_user("js@email.com", "js123!@#", "John", "Smith")
    member1 = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    token1 = creator1['token']
    u_ids1 = [member1['auth_user_id']]
    creator2 = register_user("mv@email.com", "mv123!@#", "Max", "Verstappen")
    member2 = register_user("sp@email.com", "sp123!@#", "Sergio", "Perez")
    token2 = creator2['token']
    u_ids2 = [member2['auth_user_id']]
    # Dm ID
    dm_create(token1, u_ids1)['dm_id']
    dm_id2 = dm_create(token2, u_ids2)['dm_id']
    # Dm details
    details = dm_details(token2, dm_id2)
    # User_ids
    auth_user_id_list = [creator2['auth_user_id'], member2['auth_user_id']]
    # Loop through the dm details and find if auth_user_id is in all_members
    for user in details['all_members']:
        assert(user['u_id'] in auth_user_id_list)
