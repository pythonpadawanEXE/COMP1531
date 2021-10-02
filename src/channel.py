from src.error import AccessError, InputError
from src.channels import verify_user_id
from src.data_store import data_store


def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    # Verify the user ID
    verify_user_id(auth_user_id)
    
    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            # Verify user not in channel
            if auth_user_id in channel["all_members"] or auth_user_id in channel["owner_members"]:
                raise InputError

            # Check if channel public
            elif channel["is_public"] == False:
                raise AccessError

            # Mark channel as found      
            else:
                found_channel_id = True
                target_channel = channel

    # If channel not found raise InputError
    if found_channel_id != True:
        raise InputError

    # Add user to the target_channel
    target_channel["all_members"].append(auth_user_id)
    data_store.set(store)
    return {
    }
