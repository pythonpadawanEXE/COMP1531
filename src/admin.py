from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id

def admin_user_remove_v1(auth_user_id, u_id):
    if not verify_user_id(auth_user_id):
        raise AccessError(description="User ID does not exist.")
    
    found = False
    target_user = {}
    store = data_store.get()
    users_store = store['users']
    for user in users_store:
        if u_id == user['u_id']:
            found = True
            target_user = user

    if not found:
        raise InputError(description="u_id does not refer to a valid user")

    # Purge user details
    target_user['name_first'] = 'Removed'
    target_user['name_first'] = 'user'
    target_user['email'] = ""
    target_user['handle_str'] = "Removed user"
    
    # Purge user from channel membership
    channels_store = store['channels']
    for channel in channels_store:
        channel['owner_members'].remove(u_id)
        channel['all_members'].remove(u_id)

    # Purge user from dms
    # dms_store = store['dms']
    # for dm in dms_store:
    #     dm_leave_v1(dm)

    # Purge user's message contents
    messages_store = store['messages']
    for message in messages_store:
        if message['u_id'] == u_id:
            message['message'] = "Removed user"
    
    data_store.set(store)

    return {}

def admin_userpermission_change_v1():
    pass
