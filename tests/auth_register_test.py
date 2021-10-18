from src import auth,config,other
import re
import pytest
from src.data_store import data_store
from src.error import InputError
import requests


BASE_URL = config.url

@pytest.fixture
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}
'''
Valid Input
'''

#Valid Email Test
def test_valid_email_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

def test_valid_email_1_endpoint(setup):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : 'validemail@gmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data['token'],str)
    assert response_data['auth_user_id'] == 0
    print(data_store.get())


#Valid Multiple Registrations with unique emails

def test_multiple_emails():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    assert isinstance(result1['token'],str)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Bake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    assert isinstance(result2['token'],str)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Cake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert isinstance(result3['token'],str)

    assert result2['auth_user_id'] - result1['auth_user_id'] == 1
    assert result3['auth_user_id'] - result2['auth_user_id'] == 1

#Valid Multiple Registrations with unique lowercase handles
def test_multiple_emails_valid_handles():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    assert isinstance(result1['token'],str)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    assert isinstance(result2['token'],str)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert isinstance(result3['token'],str)

    store = data_store.get()
    users = store['users']
    print(users)
    assert other.search_handle(result1['auth_user_id']) == "jakeeverest"
    assert other.search_handle(result2['auth_user_id']) == "jakeeverest0"
    assert other.search_handle(result3['auth_user_id']) == "jakeeverest1"
    
    DistinctUsers = list({Object['handle_str']:Object for Object in users}.values())
    
    print(DistinctUsers)
    assert len(users) == len(DistinctUsers)


#Valid length of password is more than 6 characters

def test_valid_len_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail3@gmail.com', 'nottooshort', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

#Valid length of name_first is  between 1 and 50 characters inclusive

def test_name_first_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail6@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

def test_name_first_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail7@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)


#Valid length of name_last is  between 1 and 50 characters inclusive

def test_name_last_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail10@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

def test_name_last_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail11@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

'''
Input Error
'''
#missing @symbol in email test
def test_invalid_email_1():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemailgmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_invalid_email_1_endpoint(setup):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : 'validemailgmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400
    

#email too long test 1
long_email = 'invalidemailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong@gmail.com'
def test_invalid_email_too_long_1():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1(long_email, '123abc!@#', 'Hayden', 'Everest')

def test_invalid_email_too_long_1_endpoint(setup):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : long_email,
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

#email too long test 2
def test_invalid_email_too_long_2():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemail@gmailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong.com', '123abc!@#', 'Hayden', 'Everest')
#email too long test 3
def test_invalid_email_too_long_3():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemailgmail.comloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', '123abc!@#', 'Hayden', 'Everest')


#Invalid Email address is already being used by another user
duplicate_email = 'duplicateemail@gmail.com'
def test_duplicate_email():
    other.clear_v1()
    auth.auth_register_v1(duplicate_email, '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        auth.auth_register_v1(duplicate_email, '123abc!@#', 'Hayden', 'Everest') # Expect fail since we already registered

def test_duplicate_endpoint(setup):

    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

#Invalid length of password is less than 6 characters

def test_invalid_short_password():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail1@gmail.com', 'short', 'Hayden', 'Everest')

def test_invalid_short_password_endpoint(setup):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : 'short',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

#Invalid length of password is more than 256 characters

def test_invalid_long_password():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail2@gmail.com', 'loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', 'Hayden', 'Everest')

#Invalid length of name_first or name_last is not between 1 and 50 characters inclusive
long_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'

@pytest.mark.parametrize("name_first", ['', long_name])
def test_name_first_invalid_length(name_first):
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail4@gmail.com', '123ab78', name_first, 'Lastname')

#endpoint test name_first
@pytest.mark.parametrize("name_first", ['', long_name])
def test_name_first_invalid_length_endpoint(setup,name_first):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123ab78',
        'name_first' : name_first,
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

@pytest.mark.parametrize("name_last", ['', long_name])
def test_name_last_invalid_length(name_last):
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail8@gmail.com', '123ab78', 'Firstname', name_last)

#endpoint test name_last
@pytest.mark.parametrize("name_last", ['', long_name])
def test_name_last_invalid_length_endpoint(setup,name_last):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123ab78',
        'name_first' : 'Hayden',
        'name_last' : name_last
    })
    assert response.status_code == 400

'''
Stress Test
'''

#Test Max Users Assumption

def test_valid_max_users_registration():
    other.clear_v1()
    for i in range(2000):
        str_name = 'John' + f'{i}'
        result = auth.auth_register_v1('validemail10'+f'{i}'+ '@gmail.com', '123ab78', 'Firstname', str_name)
        assert isinstance(result['auth_user_id'],int)
        assert isinstance(result['token'],str)

