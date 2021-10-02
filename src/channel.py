from src.error import AccessError, InputError
from src.channels import verify_user_id
from src.data_store import data_store


def channel_invite_v1(auth_user_id, channel_id, u_id):
    # Verify the user IDs
    if verify_user_id(auth_user_id) != True:
        raise AccessError

    if verify_user_id(u_id) != True:
        raise InputError
    
    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            if auth_user_id not in channel["all_members"] or auth_user_id not in channel["owner_members"]:
                raise AccessError
            
            if u_id in channel["all_members"] or u_id in channel["owner_members"]:
                raise InputError

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
    return {
    }
