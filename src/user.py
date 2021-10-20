from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id

def user_profile_v1(auth_user_id, u_id):
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

    return {
        'u_id': target_user['u_id'],
        'email' : target_user['email'],
        'name_first' : target_user['name_first'],
        'name_last'  : target_user['name_last'],
        'handle_str' : target_user['handle_str']
    }

def user_profile_setname_v1():
    pass

def user_profile_setemail_v1():
    pass

def user_profile_sethandle_v1():
    pass
