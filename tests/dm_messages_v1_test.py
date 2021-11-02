'''
dm_messages_v1_test
'''
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
    '''
    Registers a new user with given parameters and returns the users uid and token
    '''
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


# Dm creation
@pytest.fixture
def dm_endpoint():
    other.clear_v1()
    token = (register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ))['token']
    member_ids = [register_valid_user(email = 'lh@gmail.com',password = 'lh123!@#',name_first ='Lewis',name_last = 'Hamilton' )['auth_user_id']]
    return (token, member_ids)

# Another dm creation
@pytest.fixture
def another_dm_endpoint():
    other.clear_v1()
    token = (register_valid_user(email = 'mv@gmail.com',password = 'mv123!@#',name_first ='Max',name_last = 'Verstappen' ))['token']
    member_ids = [register_valid_user(email = 'sp@gmail.com',password = 'sp123!@#',name_first ='Sergio',name_last = 'Perez' )['auth_user_id']]
    return (token, member_ids)

# Create multiple messages in a dm
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

# Create multiple messages in another dm 
@pytest.fixture
def create_another_messages_endpoint(another_dm_endpoint):
    token, member_ids = another_dm_endpoint
    new_dm = create_dm_endpoint(token,member_ids)
    for i in range(5):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : new_dm['dm_id'],
        'message' : Message
    })
    return new_dm,token

# Create extrem messages in a dm
@pytest.fixture
def create_extreme_messages_endpoint(dm_endpoint):
    token, member_ids = dm_endpoint
    new_dm = create_dm_endpoint(token,member_ids)
    for i in range(60):
        Message = "message" + str(i)
        _ = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : new_dm['dm_id'],
        'message' : Message
    })
    return new_dm,token


def dm_messages_endpoint(token,dm_id,start):
    '''
    Calling dm messages to list the most recent 50 messages in dm from start index
    '''
    response = requests.get(f"{BASE_URL}/dm/messages/v1",params={
        'token' : token,
        'dm_id' : dm_id,
        'start' : start
    })
    return response.json(),response.status_code

def create_dm_endpoint(token,member_ids):
    '''
    Dm creation
    '''
    response = requests.post(f"{BASE_URL}/dm/create/v1",json={
        'token' : token,
        'u_ids' : member_ids
    })
    assert response.status_code == 200 
    return response.json()

'''
Valid start index: 0 <= start index < amount of the messages in the given dm
'''
def test_valid_start_index_in_multi_messages_endpoint(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    print(f"new_dm var {new_dm}")
    result,status_code = dm_messages_endpoint(token,new_dm['dm_id'],1)
    assert status_code == 200
    # The message is less than 50 from the start possion, the end position is not expeced.
    assert result['end'] == -1

def test_valid_message(dm_endpoint):
    msg_text = "hello, world"
    token, member_ids = dm_endpoint
    dm = create_dm_endpoint(token,member_ids)
    response = requests.post(f"{BASE_URL}/message/senddm/v1",json={
        'token' : token,
        'dm_id' : dm['dm_id'],
        'message' : msg_text
    })
    msg = response.json()
    
    dm_msgs,_ = dm_messages_endpoint(token,dm['dm_id'], 0)
    
    assert dm_msgs['messages'][0]['message_id'] == msg['message_id']

def test_valid_start_index_in_extreme_messages_endpoint(create_extreme_messages_endpoint):
    new_dm,token = create_extreme_messages_endpoint
    result,status_code = dm_messages_endpoint(token,new_dm['dm_id'], 1) 
    assert status_code == 200
    # The message is more than 50 from the start possion, the end position is expeced.
    assert result['end'] == 51

def test_dm_message_in_multi_dms(create_messages_endpoint, create_another_messages_endpoint):
    create_messages_endpoint
    dm2,token = create_another_messages_endpoint
    result,status_code = dm_messages_endpoint(token,dm2['dm_id'], 1) 
    assert status_code == 200
    assert result['end'] == -1

'''
Invalid start index: start index < 0, start index > the amount of messages in dm
'''
def test_invalid_start_index_endpoint(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    _,status_code = dm_messages_endpoint(token,new_dm['dm_id'],-1) 
    assert status_code == 400
    
def test_invalid_start_index_greater_than_messages_in_dm(create_messages_endpoint):
    new_dm,token = create_messages_endpoint
    _,status_code = dm_messages_endpoint(token,new_dm['dm_id'], 10) 
    assert status_code == 400

'''
Invalid dm refers to nonexist dm
'''
def test_invalid_dm_endpoint(dm_endpoint):
    token, _ = dm_endpoint
    _,status_code = dm_messages_endpoint(token,2,0) 
    assert status_code == 400

'''
Invalid user refers to nonexist user in the given dm 
'''
def test_invalid_user_dm_messages(create_messages_endpoint):
    new_dm,_= create_messages_endpoint
    un_authorised_user = register_valid_user(email = 'cl@gmail.com',password = 'cl123!@#',name_first ='Charles',name_last = 'Leclecr' )['token']
    _,status_code = dm_messages_endpoint(un_authorised_user,new_dm['dm_id'], 0) 
    assert status_code == 403