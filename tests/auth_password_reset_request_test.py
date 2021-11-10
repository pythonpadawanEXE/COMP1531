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

#difficult to test without frontend and email parsing
#test for bad input
def test_invalid_reset_code_password_reset_request():
    response_data = register_valid_user()
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1",json={
        'reset_code' : "123456",
        'new_password' : "123456",
    })
    assert response.status_code == 400



    
    