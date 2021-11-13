from src import auth,other,config
import re
import pytest
from src.error import InputError,AccessError
import requests
from src.data_store import data_store
from tests.helper_test_funcs import  register_valid_user,login_invalid_user,\
    login_valid_user



'''
Valid Input
'''
#test for standard login
def test_valid_login_1_endpoint():
    response_data = register_valid_user()
    assert response_data['auth_user_id'] == 0
    response_data = login_valid_user()
    assert response_data['auth_user_id'] == 0
    print(data_store.get())


#multiple  register and one login
def test_valid_login_multi_registered_endpoint():
    _ = register_valid_user()
    _ = register_valid_user(email = 'validemail1@gmail.com',password= '123abc!@#1')
    _ = register_valid_user(email = 'validemail2@gmail.com',password= '123abc!@#2')
    _ = register_valid_user(email = 'validemail3@gmail.com',password= '123abc!@#3')
    _ = register_valid_user(email = 'validemail4@gmail.com',password= '123abc!@#4')
    _ = login_valid_user()

    

#multiple logins register and login are using the same password
def test_valid_login_multi_registered_same_password_endpoint():
    _ = register_valid_user()
    _ = register_valid_user(email = 'validemail1@gmail.com')
    _ = register_valid_user(email = 'validemail2@gmail.com')
    _ = register_valid_user(email = 'validemail3@gmail.com')
    _ = register_valid_user(email = 'validemail4@gmail.com')
    _ = login_valid_user()   

#multiple logins register and login are  sequential operations
def test_multiple_logins_1_endpoint():
    _ = register_valid_user()
    _ = login_valid_user() 
    _ = register_valid_user(email = 'validemail1@gmail.com')
    _ = login_valid_user(email = 'validemail1@gmail.com') 
    _ = register_valid_user(email = 'validemail2@gmail.com')
    _ = login_valid_user(email = 'validemail2@gmail.com') 
    _ = register_valid_user(email = 'validemail3@gmail.com')
    _ = login_valid_user(email = 'validemail3@gmail.com') 
    _ = register_valid_user(email = 'validemail4@gmail.com')
    _ = login_valid_user(email = 'validemail4@gmail.com') 
    

#multiple logins register and login are not sequential operations
def test_multiple_logins_2_endpoint():
    _ = register_valid_user()
    _ = register_valid_user(email = 'validemail4@gmail.com')
    _ = register_valid_user(email = 'validemail3@gmail.com')
    _ = register_valid_user(email = 'validemail2@gmail.com')
    _ = register_valid_user(email = 'validemail1@gmail.com')
    _ = login_valid_user() 
    _ = login_valid_user(email = 'validemail1@gmail.com') 
    _ = login_valid_user(email = 'validemail2@gmail.com') 
    _ = login_valid_user(email = 'validemail3@gmail.com') 
    _ = login_valid_user(email = 'validemail4@gmail.com') 


'''
Input Errors
'''
#email login doesnt match a registered user

def test_invalid_login_email_endpoint():
    _ = register_valid_user()
    login_invalid_user(email='validemailgmail.com')


def test_invalid_login_email_2_endpoint():
    _ = register_valid_user()
    login_invalid_user(email='validemail1@gmail.com')


#login password doesnt match registered password
def test_invalid_login_password_endpoint():
    _ = register_valid_user()
    login_invalid_user(password = '123abc!@#?')

#login password doesnt match registered password with multiple registrations
def test_invalid_login_password_multi_registered_endpoint():
    _ = register_valid_user()
    _ = register_valid_user('validemail1@gmail.com', '123abc!@#1')
    _ = register_valid_user('validemail2@gmail.com', '123abc!@#2')
    _ = register_valid_user('validemail3@gmail.com', '123abc!@#3')
    _ = register_valid_user('validemail4@gmail.com', '123abc!@#4')
    login_invalid_user(password='123abc!@#?')



#login password doesnt match registered password with multiple registrations with same password
def test_invalid_login_password_multi_registered_same_password_endpoint():
    _ = register_valid_user()
    _ = register_valid_user('validemail1@gmail.com', '123abc!@#')
    _ = register_valid_user('validemail2@gmail.com', '123abc!@#')
    _ = register_valid_user('validemail3@gmail.com', '123abc!@#')
    _ = register_valid_user('validemail4@gmail.com', '123abc!@#')
    login_invalid_user(password='123abc!@#?')

