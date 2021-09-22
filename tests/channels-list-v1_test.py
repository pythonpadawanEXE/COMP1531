# channels-list-v1_test.py
# pytest file to test the implementation of channels_create_v1

import pytest
from src.channels import channels_create_v1, channels_list_v1

###################################### FIXTURES ###########################################

@pytest.fixture
def channels_same_auth_user_id():
    return ((1, 'My Channel', True), (1, 'My 2nd Channel', True), (1, 'My 3rd Channel', True))

@pytest.fixture
def channels_diff_auth_user_id():
    return ((1, 'My Channel', True), (2, 'My 2nd Channel', True), (3, 'My 3rd Channel', True))

@pytest.fixture
def make_list_of_channels(channels):
    list_of_channels = []
    for channel in channels:
        id, name, is_public = channel
        chan_id = channels_create_v1(id, name, is_public)
        list_of_channels.append({'id' : chan_id, 'name' : name})

####################################### TESTS #############################################

def test_valid_list_same_user(channels_same_auth_user_id):
    list_of_channels = make_list_of_channels(channels_same_auth_user_id)
    for channel in channels_list_v1(1):
        assert(channel in list_of_channels)

def test_valid_list_diff_user(channels_diff_auth_user_id):
    for i in len(channels_diff_auth_user_id):
        chan_id, name = channels_diff_auth_user_id[i]
        channel = {'id' : chan_id, 'name' : name}
        assert(channel in channels_list_v1(i))