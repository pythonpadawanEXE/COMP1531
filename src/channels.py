from src.data_store import data_store
from src.error import InputError, AccessError


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

# Creates a channel as specified by the parameters.
def channels_create_v1(auth_user_id, name, is_public):

    # Verifies that the user exists in the data store, raises an AccessError otherwise.
    is_authorised = False
    store = data_store.get()

    user_store = store['users']
    for user in user_store:
        if user['u_id'] == auth_user_id:
            is_authorised = True
    if is_authorised != True:
        raise AccessError

    # Verifies that the channel name is of correct length, raises an InputError otherwise.
    if len(name) < 1 or len(name) > 20:
        raise InputError

    # Creates the channel if call is valid
    # Channel dictionary entry is as follows:
    #     'id'            :   integer type - assigned sequentially
    #     'name'          :   string type
    #     'is_public'     :   boolean
    #     'owner_members' :   list of user ids - creator made an owner
    #     'all_members'   :   list of user ids - creator made a member
    else:
        channels = store['channels']
        new_channel = {
            'id': len(channels) + 1,
            'name' : name,
            'is_public' : is_public,
            'owner_members' : [auth_user_id],
            'all_members' : [auth_user_id]
            }
        channels.append(new_channel)
        data_store.set(store)

        return {
            'channel_id' : new_channel['id']
        }
            
