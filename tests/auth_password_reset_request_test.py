from requests.models import Response
from src import auth,message
import re
import pytest
from src.data_store import data_store
from src.error import InputError, AccessError
from src import other,channels,channel,config
import requests
from tests.helper_test_funcs import register_valid_user,channel_messages_endpoint,\
    create_channel_endpoint,create_message_endpoint,remove_message_endpoint,send_msg,\
        message_send_endpoint

BASE_URL = config.url

#improve coverage
def test_valid_password_reset():
    email = "dodotestuser2021t3@gmail.com"
    _ = register_valid_user(email)
    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1",json={
        'email' : email
    })
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}/get_data")
    data = response.json()
    print(data)
    reset_code = data['password_reset_codes'][0]['password_reset_code']
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1",json={
        'reset_code' : reset_code,
        'new_password' : "123456",
    })
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}/get_data")
    data = response.json()
    print(data)

#improve coverage, password too short
def test_invalid_password_reset():
    email = "dodotestuser2021t3@gmail.com"
    _ = register_valid_user(email)
    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1",json={
        'email' : email
    })
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}/get_data")
    data = response.json()
    print(data)
    reset_code = data['password_reset_codes'][0]['password_reset_code']
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1",json={
        'reset_code' : reset_code,
        'new_password' : "12345",
    })
    assert response.status_code == 400
    

#difficult to test without frontend and email parsing
#test for bad input
def test_invalid_reset_code_password_reset_request():
    _ = register_valid_user()
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1",json={
        'reset_code' : "123456",
        'new_password' : "123456",
    })
    assert response.status_code == 400



    
    