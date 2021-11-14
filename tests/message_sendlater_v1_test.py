import pytest
import requests
from time import sleep
from src import config
import datetime

@pytest.fixture(autouse=True)
def clear():

    '''
    A fixture to clear the state for each test
    '''

    response = requests.delete(config.url + "clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_user(email, password, name_first, name_last):

    '''
    Registers a new user with given parameters and returns the users token
    '''

    response = requests.post(config.url + "auth/register/v2",json={
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

    response = requests.post(config.url + "channels/create/v2", json={
        'token' : token,
        'name' : name,
        'is_public' : is_public
    })

    assert response.status_code == 200
    response_data = response.json()
    return response_data

def sendlater(token, channel_id, message, time_sent):
    '''
    Sends msg after x time
    '''
    
    response = requests.post(config.url + "message/sendlater/v1", json={
        'token' : token,
        'channel_id' : channel_id,
        'message' : message,
        'time_sent' : time_sent
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def channel_messages_endpoint(token,channel_id,start):
    response = requests.get(f"{config.url}/channel/messages/v2",params={
        'token' : token,
        'channel_id' : channel_id,
        'start' : start
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

@pytest.fixture
def setup():
    users = []
    users.append(register_user('a@email.com', 'Pass123456!', 'Jade', 'Painter'))
    users.append(register_user('b@email.com', 'Pass123456!', 'Seth', 'Tilley'))
    users.append(register_user('c@email.com', 'Pass123456!', 'Hannah', 'Buttsworth'))
    channel = channels_create(users[0]['token'], "My channel", True)
    return (users, channel)

def test_invalid_channel_id(setup):
    users, channel = setup
    response = requests.post(config.url + "message/sendlater/v1", json={
        'token' : users[0]['token'],
        'channel_id' : channel['channel_id'] + 1,
        'message' : "Hello",
        'time_sent' : int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 400

def test_invalid_channel_length(setup):
    users, channel = setup
    response = requests.post(config.url + "message/sendlater/v1", json={
        'token' : users[0]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "HelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelHelloHelloHelloloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelHelloHelloHelloloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelloHelHelloHelloHelloloHelloHelloHelloHellooHelloHelloloHelloHelloHelloHellooHelloHelloloHelloHelloHelloHellooHelloHelloloHelloHelloHelloHellooHelloHelloloHelloHelloHelloHellooHelloHelloloHelloHelloHelloHello",
        'time_sent' : int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 400

def test_invalid_time(setup):
    users, channel = setup
    response = requests.post(config.url + "message/sendlater/v1", json={
        'token' : users[0]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "Hello",
        'time_sent' : int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()) - 1
    })
    assert response.status_code == 400

def test_valid_channel_user_nonmember(setup):
    users, channel = setup
    response = requests.post(config.url + "message/sendlater/v1", json={
        'token' : users[2]['token'],
        'channel_id' : channel['channel_id'],
        'message' : "Hello",
        'time_sent' : int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())
    })
    assert response.status_code == 403

def test_valid_sendlater(setup):
    users, channel = setup
    _ = sendlater(users[0]['token'], channel['channel_id'], "Hello", int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()) + 5)
    sleep(5)
    messages = channel_messages_endpoint(users[0]['token'],channel['channel_id'],0)['messages']
    for message in messages:
        assert message['message'] == "Hello"

def test_valid_sendlater_user_handle(setup):
    users, channel = setup
    _ = sendlater(users[0]['token'], channel['channel_id'], "@sethtilley, Hello", int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()) + 5)
    sleep(5)
    messages = channel_messages_endpoint(users[0]['token'],channel['channel_id'],0)['messages']
    for message in messages:
        assert message['message'] == "@sethtilley, Hello"