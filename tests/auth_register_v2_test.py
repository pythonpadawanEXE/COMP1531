from src import auth,config,other
import re
import pytest
from src.data_store import data_store
from src.error import InputError
import requests


BASE_URL = config.url

@pytest.fixture(autouse=True)
def setup():
    #set to clear memory state for blackbox testing
    '''A fixture to clear the state for each test'''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

def register_valid_user(email = 'validemail@gmail.com',password = '123abc!@#',name_first ='Hayden',name_last = 'Everest' ):
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
    
'''
Valid Input
'''

#Valid Email Test

def test_valid_email_1_endpoint():
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
    #Valid Multiple Registrations with unique emails

def test_multiple_emails_endpoint():
    _ = register_valid_user(email = 'validemail1@gmail.com',password= '123abc!@#1')
    _ = register_valid_user(email = 'validemail2@gmail.com',password= '123abc!@#2')
    _ = register_valid_user(email = 'validemail3@gmail.com',password= '123abc!@#3')
    _ = register_valid_user(email = 'validemail4@gmail.com',password= '123abc!@#4')

#Valid Multiple Registrations with unique lowercase handles
def test_multiple_emails_valid_handles():
    _ = register_valid_user(email = 'validemail1@gmail.com',password= '123abc!@#1',name_first ='Cake')
    _ = register_valid_user(email = 'validemail2@gmail.com',password= '123abc!@#2',name_first ='Bake')
    _ = register_valid_user(email = 'validemail3@gmail.com',password= '123abc!@#3',name_first ='Lake')
    _ = register_valid_user(email = 'validemail4@gmail.com',password= '123abc!@#4',name_first ='Jake')

'''
Input Error
'''
#missing @symbol in email test
def test_invalid_email_1_endpoint():
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : 'validemailgmail.com',
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400
    

#email too long test 1
long_email = 'invalidemailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong@gmail.com'


def test_invalid_email_too_long_1_endpoint():
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : long_email,
        'password' : '123abc!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400


#Invalid Email address is already being used by another user
duplicate_email = 'duplicateemail@gmail.com'

def test_duplicate_endpoint():

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
def test_invalid_short_password_endpoint():
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : 'short',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

#Invalid length of password is more than 256 characters
long_pw = 'loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong'
def test_invalid_long_password_endpoint():
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : long_pw,
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    assert response.status_code == 400

#Invalid length of name_first or name_last is not between 1 and 50 characters inclusive
long_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'

#endpoint test name_first
@pytest.mark.parametrize("name_first", ['', long_name])
def test_name_first_invalid_length_endpoint(name_first):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123ab78',
        'name_first' : name_first,
        'name_last' : 'Everest'
    })
    assert response.status_code == 400



#endpoint test name_last
@pytest.mark.parametrize("name_last", ['', long_name])
def test_name_last_invalid_length_endpoint(name_last):
    response = requests.post(f"{BASE_URL}/auth/register/v2",json={
        'email' : duplicate_email,
        'password' : '123ab78',
        'name_first' : 'Hayden',
        'name_last' : name_last
    })
    assert response.status_code == 400



