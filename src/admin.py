from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import is_global_owner, verify_user_id

def get_global_owners():
    store = data_store.get()
    users_store = store['users']
    global_owners = []
    for user in users_store:
        if user['permission_id'] == 1:
            global_owners.append(user)
    return global_owners

def admin_user_remove_v1(auth_user_id, u_id):
    if not verify_user_id(auth_user_id):
        raise AccessError(description="User ID does not exist.")

    if not is_global_owner(auth_user_id):
        raise AccessError(description="The authorised user is not a global owner")

    global_owners = get_global_owners()
    if len(global_owners) == 1 and global_owners[0]['u_id'] == u_id:
        raise InputError(description="u_id refers to a user who is the only global owner")
    
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

def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):
    if not verify_user_id(auth_user_id):
        raise AccessError(description="User ID does not exist.")

    if not is_global_owner(auth_user_id):
        raise AccessError(description="The authorised user is not a global owner")

    if permission_id != 1 and permission_id != 2:
        raise InputError(description="permission_id is invalid")

    global_owners = get_global_owners()
    if len(global_owners) == 1 and global_owners[0]['u_id'] == u_id and permission_id == 2:
        raise InputError(description="u_id refers to a user who is the only global owner")
    
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
        
    target_user['permission_id'] = permission_id

    data_store.set(store)

    return {}

