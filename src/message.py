from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_valid_token

def message_send_v1(token, channel_id, message_input):
    auth_user_id = check_valid_token(token)['auth_user_id']
    len_msg = len(message_input)
    if len_msg < 1 or len_msg > 1000:
        raise InputError("Invalid Length of Message.")
    store = data_store.get()
    channels = store['channels']
    messages = None
    channel_exists = False
    for channel in channels:
        if channel['id'] == channel_id:
            channel_exists = True
            if auth_user_id not in channel["all_members"] and \
                auth_user_id not in channel["owner_members"]:
                raise AccessError("User is not an owner or member of this channel.")
            messages = channel['messages']
            break

    if not channel_exists:
        raise InputError("Channel ID is not valid or does not exist.")

    for message in messages:
        message['message_id'] += 1

    messages.insert(0,
        {
            'message_id': 0,
            'u_id': auth_user_id,
            'message': message_input,
            'time_created': int(datetime.datetime.utcnow()
                            .replace(tzinfo= datetime.timezone.utc).timestamp()),
        }
    )
    data_store.set(store)