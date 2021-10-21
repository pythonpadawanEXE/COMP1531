from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token, verify_user_id, generate_dm_name

def dm_create_v1(auth_user_id, u_ids):
    creator_u_id = auth_user_id
    all_members = [creator_u_id]
    for u_id in u_ids:
        if not verify_user_id(u_id):
            raise InputError(description ="User not exist.")
        all_members.append(u_id)
    store = data_store.get()
    dms = store['dms']
    
    new_dm = {
        'dm_id' : len(dms) + 1,
        'name' : generate_dm_name(all_members),
        'owner' : [creator_u_id],
        'all_members' : all_members,
        'messages' : [],
    }

    dms.append(new_dm)
    data_store.set(store)
    return{'dm_id': new_dm['dm_id']}

def dm_list_v1(auth_user_id):
    store = data_store.get()
    dm_store= store['dms']
    dms = []

    for dm in dm_store:
        if auth_user_id in dm['all_members']:
            dms.append({'dm_id' : dm['dm_id'], 'name' : dm['name']})

    return{
        'dms' : dms
    }

def dm_leave_v1(token, dm_id)
    
    if not is_dm_valid(dm_id):
        raise InputError(description ="Dm not exist.")
        
    store = data_store.get()
    dm_store= store['dms']
    
    if not auth_user_id in dm_store['all_members']:
        raise AccessError(description ="Could not find user in this dm.")
    
    for dm in dm_store:
        if dm['id'] == dm_id:
            dm['all_members'].remove(auth_user_id)
    return {}
