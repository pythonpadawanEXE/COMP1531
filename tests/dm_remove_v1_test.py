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
    Creates a dm with given token and members' u_ids returns the dm ID
    '''
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : token,
        'u_ids' : u_ids,
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_list(token):
    '''
    Calling dm list to check basic information of dms of the given user in
    '''
    response = requests.get(f"{BASE_URL}dm/list/v1?token={token}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def dm_remove(token, dm_id):
    '''
    Removes a user with token to dm with dm_id
    '''
    response = requests.delete(f"{BASE_URL}dm/remove/v1", json={
        'token' : token,
        'dm_id' : dm_id,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

'''
Valid remove requires the owner of the given dm to operate successfully.
'''  
def test_valid_remove():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']

    member_u_ids = [member['auth_user_id']]
    # Dm ID
    dm_id = dm_create(creator_token, member_u_ids)['dm_id']
    
    list_before = dm_list(creator_token)
     # Dm should be in creator's dm before remove
    assert (list_before) == {'dms': [{'dm_id': dm_id, 'name': 'johnsmith, lewishamilton'}]}
    # Remove dm from dms
    dm_remove(creator_token, dm_id)
    #Dm list of the creator
    list_after = dm_list(creator_token)
    # Dm should not exist in creator's dm list any longer
    assert(list_after) == {'dms':[]}

'''
Valid remove requires the owner of the given dm to operate successfully.
The member of the given dm is not able to operate the dm remove.
An AccessError would be expected to be raised when member of the given dm doing the operation.
'''  
def test_member_remove():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_token = member['token']
    member_u_ids = [member['auth_user_id']]
    dm_id = dm_create(creator_token, member_u_ids)['dm_id']
    # AccessError is expected to be raised for a member doing the remove operaton
    response = requests.delete(f"{BASE_URL}dm/remove/v1", json={
        'token' : member_token,
        'dm_id' : dm_id,
    })
    assert response.status_code == 403

'''
Invalid dm refers to a nonexist dm
'''
def test_invalid_dm_remove():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member1 = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    creator_token = creator['token']
    member_u_ids = [member1['auth_user_id']]
    dm_create(creator_token, member_u_ids)['dm_id']
    # Input error is expected to be raised for a invalid dm
    response = requests.delete(f"{BASE_URL}dm/remove/v1", json={
        'token' : creator_token,
        'dm_id' : '999',
    })
    assert response.status_code == 400
    
def test_valid_dm_remove_multi_dms():
    # New users
    creator = register_user("js@email.com", "js123!@#", "John", "Smith")
    member1 = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    member2 = register_user("cl@email.com", "cl123!@#", "Charles", "Leclerc")
    creator_token = creator['token']
   
    dm1_member_list = [member1['auth_user_id'], member2['auth_user_id']]
    dm2_member_list = [member1['auth_user_id']]
    # Dm IDs
    dm1_id = dm_create(creator_token, dm1_member_list)['dm_id']
    dm2_id = dm_create(creator_token, dm2_member_list)['dm_id']

    list_before = dm_list(creator_token)
     # Dm should be in creator's dm before remove the given dm 
    assert (list_before) == {'dms': [{'dm_id': dm1_id, 'name': 'charlesleclerc, johnsmith, lewishamilton'}, 
                                        {'dm_id': dm2_id, 'name': 'johnsmith, lewishamilton'}]}
    # Remove dm from dms
    dm_remove(creator_token, dm2_id)
    # Dm list of the creator after remove the given dm 
    list_after = dm_list(creator_token)
    # The given dm should not exist in creator's dm list any longer
    assert(list_after) == {'dms': [{'dm_id': dm1_id, 'name': 'charlesleclerc, johnsmith, lewishamilton'}]}

def test_ivalid_dm_remove_creator_of_another_dm():
    # New users
    creator1 = register_user("js@email.com", "js123!@#", "John", "Smith")
    creator2 = register_user("mv@email.com", "mv123!@#", "Max", "Vertappen")
    member1 = register_user("lw@email.com", "lw123!@#", "Lewis", "Hamilton")
    member2 = register_user("cl@email.com", "cl123!@#", "Charles", "Leclerc")
    creator1_token = creator1['token']
    creator2_token = creator2['token']
    dm1_member_list = [member1['auth_user_id'], member2['auth_user_id']]
    dm2_member_list = [member1['auth_user_id']]
    # Dm IDs
    dm_create(creator1_token, dm1_member_list)['dm_id']
    dm2_id = dm_create(creator2_token, dm2_member_list)['dm_id']
    # Valid remove requires the owner of the given dm to operate successfully.
    response = requests.delete(f"{BASE_URL}dm/remove/v1", json={
        'token' : creator1_token,
        'dm_id' : dm2_id,
    })
    # AccessError is expected to be raised for a creator of another dm doing the remove operaton for the given dm
    assert response.status_code == 403
    