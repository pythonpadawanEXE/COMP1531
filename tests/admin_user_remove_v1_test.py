# admin_user_remove_v1_test.py
# pytest file to test the implementation of admin_user_remove_v1
import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users.
    '''
    users = []
    requests.delete(config.url + 'clear/v1')
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    users.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail2@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Robert',
        'name_last' : 'Reid'
    })
    users.append(json.loads(resp.text))
    resp = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'validemail3@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Jade',
        'name_last' : 'Painter'
    })
    users.append(json.loads(resp.text))
    return users

def test_user_not_global_owner(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': users[1]['token'], 'u_id': users[2]['auth_user_id']})
    assert resp.status_code == 403

def test_u_id_not_valid(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': users[0]['token'], 'u_id': 7896})
    assert resp.status_code == 400

def test_u_id_only_global_owner(setup):
    users = setup
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': users[0]['token'], 'u_id': users[0]['auth_user_id']})
    assert resp.status_code == 400

def test_valid_removal(setup):
    users = setup
    channel = requests.post(config.url + 'channels/create/v2', json={'token': users[0]['token'], 'name': 'My Channel', 'is_public': True})
    priv_channel = requests.post(config.url + 'channels/create/v2', json={'token': users[0]['token'], 'name': 'My private Channel', 'is_public': False})
    channel_id = json.loads(channel.text)['channel_id']
    priv_channel_id = json.loads(priv_channel.text)['channel_id']
    _ = requests.post(config.url + 'channel/join/v2', json={'token': users[1]['token'], 'channel_id': channel_id})

    # User sends message in channel
    _ = requests.post(config.url + 'message/send/v1', json={'token': users[1]['token'], 'channel_id': channel_id, 'message': 'Hello World!'})
    _ = requests.post(config.url + 'message/send/v1', json={'token': users[0]['token'], 'channel_id': priv_channel_id, 'message': 'Hello Private World!'})
    # User sends message in dm
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': users[0]['token'], 'u_ids': [users[1]['auth_user_id']]})
    dm_id = json.loads(dm_create.text)['dm_id']
    _ = requests.post(config.url + 'message/senddm/v1', json={'token': users[1]['token'], 'dm_id': dm_id, 'message': 'Hello world!'})

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    assert resp.status_code == 200

    # Check user profile
    profile = requests.get(config.url + 'user/profile/v1', params={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    removed_profile = json.loads(profile.text)['user']
    assert removed_profile['name_first'] == "Removed"
    assert removed_profile['name_last'] == "user"

    # Check user in any channels
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': users[0]['token'], 'channel_id': channel_id})
    channel_membership = json.loads(channel_details.text)['all_members']
    assert {'u_id': users[1]['auth_user_id'], 'email' : 'validemail2@gmail.com', 'name_first' : 'Robert', 'name_last' : 'Reid', 'handle_str': 'robertreid'} not in channel_membership

    # Check user in any dms
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': users[0]['token'], 'dm_id': dm_id})
    dm_membership = json.loads(dm_details.text)['members']
    assert {'u_id': users[1]['auth_user_id'], 'email' : 'validemail2@gmail.com', 'name_first' : 'Robert', 'name_last' : 'Reid', 'handle_str': 'robertreid'} not in dm_membership

    # Check channel message history for user
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': users[0]['token'], 'channel_id': channel_id, 'start': 0})
    messages = json.loads(channel_messages.text)['messages']
    assert messages[0]['message'] == "Removed user"

    # Check dm message history for user
    dm_messages = requests.get(config.url + 'dm/messages/v1', params={'token': users[0]['token'], 'dm_id': dm_id, 'start': 0})
    messages = json.loads(dm_messages.text)['messages']
    assert messages[0]['message'] == "Removed user"

    # Check user not listed in all users
    users_list = requests.get(config.url + 'users/all/v1', params={'token': users[0]['token']})
    users_list = json.loads(users_list.text)
    for user in users_list:
        assert {'u_id': users[1]['auth_user_id'], 'email' : '', 'name_first' : 'Removed', 'name_last' : 'user', 'handle_str': 'Removed user'} != user
    
    # Check removed user cannot do anything
    resp = requests.get(config.url + 'users/all/v1', params={'token': users[1]['token']})
    assert resp.status_code == 403
    
    # Check profile exists
    resp = requests.get(config.url + 'user/profile/v1', params={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    response_data = resp.json()['user']
    assert response_data == {'u_id': users[1]['auth_user_id'], 'email': '', 'name_first': 'Removed', 'name_last': 'user', 'handle_str': 'Removed user'}

def test_valid_removal_channel_owner(setup):
    users = setup
    channel = requests.post(config.url + 'channels/create/v2', json={'token': users[0]['token'], 'name': 'My Channel', 'is_public': True})
    priv_channel = requests.post(config.url + 'channels/create/v2', json={'token': users[0]['token'], 'name': 'My private Channel', 'is_public': False})
    channel_id = json.loads(channel.text)['channel_id']
    priv_channel_id = json.loads(priv_channel.text)['channel_id']
    _ = requests.post(config.url + 'channel/join/v2', json={'token': users[1]['token'], 'channel_id': channel_id})

    # Make user a channel owner
    _ = requests.post(config.url + 'channel/addowner/v1', json={'token': users[0]['token'], 'channel_id': channel_id, 'u_id': users[1]['auth_user_id']})

    # User sends message in channel
    _ = requests.post(config.url + 'message/send/v1', json={'token': users[1]['token'], 'channel_id': channel_id, 'message': 'Hello World!'})
    _ = requests.post(config.url + 'message/send/v1', json={'token': users[0]['token'], 'channel_id': priv_channel_id, 'message': 'Hello Private World!'})
    

    # User sends message in dm
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': users[0]['token'], 'u_ids': [users[1]['auth_user_id']]})
    dm_id = json.loads(dm_create.text)['dm_id']
    _ = requests.post(config.url + 'message/senddm/v1', json={'token': users[1]['token'], 'dm_id': dm_id, 'message': 'Hello world!'})

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    assert resp.status_code == 200

    # Check user profile
    profile = requests.get(config.url + 'user/profile/v1', params={'token': users[0]['token'], 'u_id': users[1]['auth_user_id']})
    removed_profile = json.loads(profile.text)['user']
    assert removed_profile['name_first'] == "Removed"
    assert removed_profile['name_last'] == "user"

    # Check user in any channels
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': users[0]['token'], 'channel_id': channel_id})
    channel_membership = json.loads(channel_details.text)['all_members']
    assert {'u_id': users[1]['auth_user_id'], 'email' : 'validemail2@gmail.com', 'name_first' : 'Robert', 'name_last' : 'Reid', 'handle_str': 'robertreid'} not in channel_membership

    # Check user in any dms
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': users[0]['token'], 'dm_id': dm_id})
    dm_membership = json.loads(dm_details.text)['members']
    assert {'u_id': users[1]['auth_user_id'], 'email' : 'validemail2@gmail.com', 'name_first' : 'Robert', 'name_last' : 'Reid', 'handle_str': 'robertreid'} not in dm_membership

    # Check channel message history for user
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={'token': users[0]['token'], 'channel_id': channel_id, 'start': 0})
    print(channel_messages.json())
    messages = json.loads(channel_messages.text)['messages']
    assert messages[0]['message'] == "Removed user"

    # Check dm message history for user
    dm_messages = requests.get(config.url + 'dm/messages/v1', params={'token': users[0]['token'], 'dm_id': dm_id, 'start': 0})
    messages = json.loads(dm_messages.text)['messages']
    assert messages[0]['message'] == "Removed user"

    # Check user not listed in all users
    users_list = requests.get(config.url + 'users/all/v1', params={'token': users[0]['token']})
    users_list = json.loads(users_list.text)
    for user in users_list:
        assert {'u_id': users[1]['auth_user_id'], 'email' : '', 'name_first' : 'Removed', 'name_last' : 'user', 'handle_str': 'Removed user'} != user
