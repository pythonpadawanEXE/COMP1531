# channels-list-v1_test.py
# pytest file to test the implementation of channels_list_v1

from src.error import AccessError
import pytest

from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_list_v1

def test_valid_list():
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']
    list_of_channels = []
    list_of_channels.append(channels_create_v1(auth_user_id_1, "Chan 1", True))
    list_of_channels.append(channels_create_v1(auth_user_id_1, "Chan 2", True))
    list_of_channels.append(channels_create_v1(auth_user_id_1, "Chan 3", True))
    bad_chan = channels_create_v1(auth_user_id_2, "Chan 4", True)
    channels = channels_list_v1(auth_user_id_1)
    for channel in list_of_channels:
        assert(channel in channels)
    assert(bad_chan not in channels)

def test_raise_exception(): 
    with pytest.raises(AccessError):
        assert(channels_list_v1(687543) == [])

