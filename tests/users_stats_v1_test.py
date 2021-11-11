import pytest
import requests
import json
from src import config

BASE_URL = config.url

@pytest.fixture
def setup():
    '''
    Clears the server data and creates some users and channels.
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

def channel_create_endpoint(token,name,is_public):
    response = requests.post(f"{BASE_URL}/channels/create/v2",json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })
    assert response.status_code == 200 
    return response.json()

def dm_create_endpoint(token, u_ids):
    response = requests.post(f"{BASE_URL}dm/create/v1", json={
        'token' : token,
        'u_ids' : u_ids,
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def send_message_channel(token,channel_id,message):
    response = requests.post(f"{BASE_URL}/message/send/v1",json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message
    })
    return response.json(),response.status_code

def send_message_dm(token,dm_id,message):
    response = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : dm_id,
        'message' : message
        })
    return response.json(),response.status_code

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

def message_remove(token,message_id):
    response = requests.delete(f"{BASE_URL}/message/remove/v1",json={
        'token' : token,
        'message_id' : message_id,
    })
    return response.json(),response.status_code

def users_stats(token):
    response = requests.get(f"{BASE_URL}users/stats/v1?token={token}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def test_valid_user_stats(setup):
    users = setup
    channel_create_endpoint(users[0]['token'], 'channel1', True)
    dm_create_endpoint(users[1]['token'],[users[0]['auth_user_id']])
    send_message_channel(users[0]['token'], 1 ,"Hello world")
    send_message_dm(users[1]['token'], 1, "Hello world")
    stats = users_stats(users[1]['token'])

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['dms_exist'][1]['num_dms_exist'] == 1
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['messages_exist'][2]['num_messages_exist'] == 2
    assert stats['utilization_rate'] == float(2/3)

def test_valid_user_stats_dm_remove(setup):
    users = setup
    channel_create_endpoint(users[0]['token'], 'channel1', True)
    dm_create_endpoint(users[1]['token'],[users[0]['auth_user_id']])
    send_message_channel(users[0]['token'], 1 ,"Hello world")
    send_message_dm(users[1]['token'], 1, "Hello world")
    dm_remove(users[1]['token'],1)
    stats = users_stats(users[1]['token'])

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['dms_exist'][1]['num_dms_exist'] == 1
    assert stats['dms_exist'][2]['num_dms_exist'] == 0
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['messages_exist'][2]['num_messages_exist'] == 2
    assert stats['utilization_rate'] == float(1/3)

def test_valid_user_stats_message_remove(setup):
    users = setup
    channel_create_endpoint(users[0]['token'], 'channel1', True)
    dm_create_endpoint(users[1]['token'],[users[0]['auth_user_id']])
    send_message_channel(users[0]['token'], 1 ,"Hello world")
    send_message_dm(users[1]['token'], 1, "Hello world")
    message_remove(users[0]['token'], 0)
    stats = users_stats(users[1]['token'])

    assert stats['channels_exist'][0]['num_channels_exist'] == 0
    assert stats['dms_exist'][0]['num_dms_exist'] == 0
    assert stats['dms_exist'][1]['num_dms_exist'] == 1
    assert stats['messages_exist'][0]['num_messages_exist'] == 0
    assert stats['messages_exist'][1]['num_messages_exist'] == 1
    assert stats['messages_exist'][2]['num_messages_exist'] == 2
    assert stats['messages_exist'][3]['num_messages_exist'] == 1
    assert stats['utilization_rate'] == float(2/3)

