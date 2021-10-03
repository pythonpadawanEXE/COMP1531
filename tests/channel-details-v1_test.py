# channels-details-v1_test.py
# pytest file to test the implementation of channel_details_v1

import pytest

from src.error import AccessError
from src.error import InputError

from src.auth import auth_register_v1
from src.channel import channel_invite_v1, channel_details_v1, channel_join_v1
from src.channels import channels_create_v1
from src.other import clear_v1

# Test for a single member with a public channel
def test_details_public_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    # Channel ID
    channel_id = channels_create_v1(auth_user_id, "Chan 1", True)['channel_id']
    # Channel details
    channel_details = channel_details_v1(auth_user_id, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in channel_details['all_members']:
        assert(auth_user_id == user['u_id'])

# Test for a single member with a private channel
def test_details_private_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    # Channel ID
    channel_id = channels_create_v1(auth_user_id, "Chan 1", False)['channel_id']
    # Channel details
    channel_details = channel_details_v1(auth_user_id, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in channel_details['all_members']:
        assert(auth_user_id == user['u_id'])

# Test for a single member with public and private channels
def test_details_mixed_individual():
    clear_v1()

    # New user
    auth_user_id = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    # Channel ID
    channel_id = channels_create_v1(auth_user_id, "Chan 1", False)['channel_id']
    # Create a public channel
    channels_create_v1(auth_user_id, "Chan 2", True)['channel_id']
    # Channel details
    channel_details = channel_details_v1(auth_user_id, channel_id)

    # Loop through the channel details and find if auth_user_id is in all_members
    for user in channel_details['all_members']:
        assert(auth_user_id == user['u_id'])

# Test for multiple members with a public channel
def test_details_public_multiple():
    clear_v1()

    # New user
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    # New user 2
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']

    # Channel ID
    channel_id = channels_create_v1(auth_user_id_1, "Chan 1", True)['channel_id']
    # Invite auth_user_id_2 to channel
    channel_join_v1(auth_user_id_2, channel_id)
    # Channel details
    channel_details = channel_details_v1(auth_user_id_1, channel_id)

    # Loop through the channel details and find if auth_user_id and auth_user_id2 is in the channel
    for user in channel_details['all_members']:
        assert(auth_user_id_1 == user['u_id'] or auth_user_id_2 == user['u_id'])

# Test for invalid channel ID
def test_invalid_channel():
    clear_v1()
    # New user
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    with pytest.raises(InputError):
        assert(channel_details_v1(auth_user_id_1, 9999))

# Test for valid channel ID and the authorised user is not a member of the channel
def test_user_unauthorised():
    clear_v1()

    # New user
    auth_user_id_1 = auth_register_v1("js@email.com", "ABCDEFGH", "John", "Smith")['auth_user_id']
    # New user 2
    auth_user_id_2 = auth_register_v1("jems@email.com", "ABCDEFGH", "Jemma", "Smith")['auth_user_id']
    # Channel ID
    channel_id = channels_create_v1(auth_user_id_1, "Chan 1", True)['channel_id']

    with pytest.raises(AccessError):
        assert(channel_details_v1(auth_user_id_2, channel_id))