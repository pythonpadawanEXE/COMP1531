from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id

def users_all_v1(auth_user_id):
    if not verify_user_id(auth_user_id):
        raise AccessError(description="User ID does not exist.")

    store = data_store.get()
    users_store = store['users']
    users = {'users' : []}
    for user in users_store:
        users['users'].append({
            'u_id': user['u_id'],
            'email' : user['email'],
            'name_first' : user['name_first'],
            'name_last'  : user['name_last'],
            'handle_str' : user['handle_str']
        })

    return users
