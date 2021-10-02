# channels-create-v1_test.py
# pytest file to test the implementation of channel_join_v1

import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_join_v1, channel_details_v1
from src.other import clear_v1
from src.error import AccessError, InputError

def test_invalid_channel_id():
    clear_v1()
    user = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    with pytest.raises(InputError):
        assert(channel_join_v1(user["auth_user_id"], 999) == {})

def test_already_joined():
    clear_v1()
    user = auth_register_v1("b@email.com", "ABCDEF123", "Cal", "Watts")
    channel = channels_create_v1(user["auth_user_id"], "Channel 1", True)
    with pytest.raises(InputError):
        assert(channel_join_v1(user["auth_user_id"], channel["channel_id"]) == {})

def test_join_private_channel():
    owner = auth_register_v1("c@email.com", "ABCDEF123", "Cal", "Watts")
    user = auth_register_v1("d@email.com", "ABCDEF123", "Kim", "Smith")
    channel = channels_create_v1(owner["auth_user_id"], "Channel 1", False)
    with pytest.raises(AccessError):
        assert(channel_join_v1(user["auth_user_id"], channel["channel_id"]) == {})

def test_join_public_channel():
    owner = auth_register_v1("e@email.com", "ABCDEF123", "Cal", "Watts")
    user = auth_register_v1("f@email.com", "ABCDEF123", "Kim", "Smith")
    channel = channels_create_v1(owner["auth_user_id"], "Channel 1", True)
    assert(channel_join_v1(user["auth_user_id"], channel["channel_id"]) == {})
    assert(user["auth_user_id"] in channel_details_v1(owner["auth_user_id"], channel["channel_id"])["all_members"])