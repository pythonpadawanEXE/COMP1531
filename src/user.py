from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, check_valid_token

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

def user_profile_setname_v1(token, name_first, name_last):

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    length_name_first = len(name_first)
    length_name_last = len(name_last)

    # Verify user ID
    if not verify_user_id(u_id):
        raise AccessError(description="u_id does not exist.")

    # length of name_first is not between 1 and 50 characters inclusive
    if (length_name_first < 1 or length_name_first > 50):
        raise InputError(description="length of name_first is not between 1 and 50 characters inclusive")

    # length of name_last is not between 1 and 50 characters inclusive
    if (length_name_last < 1 or length_name_last > 50):
        raise InputError(description="length of name_last is not between 1 and 50 characters inclusive")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update users name
            user['name_first'] = name_first
            user['name_last'] = name_last

    data_store.save()

    return {}

def user_profile_setemail_v1():
    pass

def user_profile_sethandle_v1():
    pass
