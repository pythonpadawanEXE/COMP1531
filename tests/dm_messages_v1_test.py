
import pytest
from src import other,config
import requests



BASE_URL = config.url

@pytest.fixture(autouse=True)
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}


def register_valid_user(email, password, name_first, name_last):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
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
def dm_endpoint():
    other.clear_v1()
    token = (register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ))['token']
    member_ids = [register_valid_user(email = 'lh@gmail.com',password = 'lh123!@#',name_first ='Lewis',name_last = 'Hamilton' )['auth_user_id']]
    return (token, member_ids)


#create multiple messages in a public channel
@pytest.fixture
def create_messages_endpoint(dm_endpoint):
    token, member_ids = dm_endpoint
    new_dm = create_dm_endpoint(token,member_ids)
    for i in range(5):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : new_dm['dm_id'],
        'message' : Message
    })
    return new_dm,token



def dm_messages_endpoint(token,dm_id,start):
    response = requests.get(f"{BASE_URL}/dm/messages/v1",params={
        'token' : token,
        'dm_id' : dm_id,
        'start' : start
    })
    return response.json(),response.status_code

def create_dm_endpoint(token,member_ids):
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : token,
        'u_ids' : member_ids
    })
    assert response.status_code == 200 
    return response.json()

"""
Valid Input
"""

#start is not greater than the total number of messages in the channel

def test_valid_start_index_endpoint(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    print(f"new_dm var {new_dm}")
    result,status_code = dm_messages_endpoint(token,new_dm['dm_id'],1)
    assert status_code == 200
    assert result["end"] == -1


"""
Input Errors
"""

#start is not less than 0
def test_invalid_negative_start_index_endpoint(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    _,status_code = dm_messages_endpoint(token,new_dm['dm_id'],-1) 
    assert status_code == 400
    


def test_invalid_dm_1_endpoint(dm_endpoint):
    token, _ = dm_endpoint
    _,status_code = dm_messages_endpoint(token,2,0) 
    assert status_code == 400



def test_start_greater_than_num_messages(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    _,status_code = dm_messages_endpoint(token,new_dm['dm_id'], 10) 
    assert status_code == 400
