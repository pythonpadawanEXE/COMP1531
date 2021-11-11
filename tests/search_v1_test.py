# search_v1_test.py
# pytest file to test the implementation of search/v1 endpoint

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

def register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ):
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

#user public channel 
@pytest.fixture
def pub_chan_endpoint():
    other.clear_v1()
    token = (register_valid_user())['token']
    return (token, 'My Channel', True)

#create multiple messages in a public channel
@pytest.fixture
def create_messages_endpoint(pub_chan_endpoint):
    token, name, is_public = pub_chan_endpoint
    new_channel = create_channel_endpoint(token,name,is_public)
    for i in range(5):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}message/send/v1",json={
        'token' : token,
        'channel_id' : new_channel['channel_id'],
        'message' : Message
    })
    return new_channel,token

# Returns DM id
def dm_create_endpoint(token, u_ids):
    response = requests.post(f"{BASE_URL}dm/create/v1",json={
        'token' : token,
        'u_ids' : u_ids
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

# Returns DM message ID
def dm_sendmsg(token, dm_id, message):
    response = requests.post(f"{BASE_URL}message/senddm/v1",json={
        'token' : token,
        'dm_id' : dm_id,
        'message' : message
    })
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def search_endpoint(token, query):
    response = requests.get(f"{BASE_URL}search/v1?token={token}&query={query}")
    assert response.status_code == 200
    response_data = response.json()
    return response_data

def test_valid_search(create_messages_endpoint):
    new_channel,token = create_messages_endpoint
    response_data = search_endpoint(token, "message")

    assert response_data[0]['message'] == 'message0'
    assert response_data[1]['message'] == 'message1'
    assert response_data[2]['message'] == 'message2'
    assert response_data[3]['message'] == 'message3'
    assert response_data[4]['message'] == 'message4'

def test_invalid_search(create_messages_endpoint):
    new_channel,token = create_messages_endpoint

    response = requests.get(f"{BASE_URL}search/v1?token={token}&query={''}")
    assert response.status_code == 400

    response = requests.get(f"{BASE_URL}search/v1?token={token}&query={'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum volutpat nulla massa, in laoreet magna blandit id. Vivamus vitae magna sit amet lorem commodo tincidunt sed id risus. Pellentesque finibus mollis efficitur. Ut id risus eget justo rhoncus feugiat. Vivamus commodo urna id augue placerat vestibulum in ut sapien. Phasellus tempus dignissim finibus. Nullam nulla velit, lobortis eu auctor ut, faucibus id risus. Donec non erat quam. Cras accumsan a mi eu pellentesque. Nullam ultricies egestas commodo. Morbi gravida risus at condimentum auctor. Suspendisse mi quam, ultrices eget rhoncus et, sodales vitae lacus. Nam sed mattis massa, ac fringilla nulla. Nam sed imperdiet augue. Sed eu velit nisl. Quisque dignissim nulla sodales sem pellentesque. Nullam ultricies egestas commodo. Morbi gravida risus at condimentum auctor. Suspendisse mi quam, ultrices eget rhoncus et, sodales vitae lacus. Nam sed mattis massa, ac fringilla nulla. Nam sed imperdiet augue. Sed eu velit nisl. Quisque dignissim nulla sodales sem'}")
    assert response.status_code == 400

def test_valid_searh_dm():
    user1 = register_valid_user()
    token1 = user1['token']
    id1 = user1['auth_user_id']

    user2 = register_valid_user()
    token2 = user2['token']
    id2 = user2['auth_user_id']

    u_ids = [id2]
    dm_id = dm_create_endpoint(token1, u_ids)['dm_id']
    dm_sendmsg(token, dm_id, "Message123")

    response_data = search_endpoint(token1, "message")

    assert response_data[0]['message'] == 'Message123'