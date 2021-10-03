# channel_invite_v1_test.py
# pytest file to test the implementation of channel_invite_v1

import pytest
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_invite_v1, channel_details_v1
from src.other import clear_v1
from src.error import AccessError, InputError

def test_invalid_channel_id():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    user_b = auth_register_v1("d@email.com", "ABCDEF123", "Kim", "Smith")
    with pytest.raises(InputError):
        assert(channel_invite_v1(user_a["auth_user_id"], 999, user_b["auth_user_id"]) == {})

def test_invalid_u_id():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    channel = channels_create_v1(user_a["auth_user_id"], "Channel 1", True)
    with pytest.raises(InputError):
        assert(channel_invite_v1(user_a["auth_user_id"], channel["channel_id"], 999) == {})

def test_u_id_a_member():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    channel = channels_create_v1(user_a["auth_user_id"], "Channel 1", True)
    with pytest.raises(InputError):
        assert(channel_invite_v1(user_a["auth_user_id"], channel["channel_id"], user_a["auth_user_id"]) == {})

def test_auth_user_not_member():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    user_b = auth_register_v1("d@email.com", "ABCDEF123", "Kim", "Smith")
    channel = channels_create_v1(user_a["auth_user_id"], "Channel 1", True)
    with pytest.raises(AccessError):
        assert(channel_invite_v1(user_b["auth_user_id"], channel["channel_id"], user_a["auth_user_id"]) == {})

def test_bad_auth_user_id():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    channel = channels_create_v1(user_a["auth_user_id"], "Channel 1", True)
    with pytest.raises(AccessError):
        assert(channel_invite_v1(999, channel["channel_id"], user_a["auth_user_id"]) == {})

def test_valid_invite():
    clear_v1()
    user_a = auth_register_v1("a@email.com", "ABCDEF123", "Cal", "Watts")
    user_b = auth_register_v1("d@email.com", "ABCDEF123", "Kim", "Smith")
    channel = channels_create_v1(user_a["auth_user_id"], "Channel 1", True)
    assert(channel_invite_v1(user_a["auth_user_id"], channel["channel_id"], user_b["auth_user_id"]) == {})
    list_of_members = channel_details_v1(user_b["auth_user_id"], channel["channel_id"])["all_members"]
    list_of_ids = []
    for member in list_of_members:
        list_of_ids.append(member["u_id"])
    assert(user_b["auth_user_id"] in list_of_ids)