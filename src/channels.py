from src.data_store import data_store
from src.error import InputError

def channels_list_v1(auth_user_id):
    store = data_store.get()
    channel_store = store['channels']
    channels = []
    for chan in channel_store:
        if auth_user_id in chan['all_members']:
            channels.append({'channel_id' : chan['id'], 'name' : chan['name']})
    return channels

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    if len(name) < 1 or len(name) > 20:
        raise InputError
        return None

    else:
        store = data_store.get()
        channels = store['channels']
        new_channel = {
            'id': len(channels) + 1,
            'name' : name,
            'is_public' : is_public,
            'owner_members' : [auth_user_id],
            'all_members' : [auth_user_id]
            }
        data_store.set(store)

        return int(new_channel['id'])
