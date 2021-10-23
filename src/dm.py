from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, generate_dm_name, is_dm_valid, get_all_user_id_dm, get_dm_name, is_user_authorised_dm, get_dm_owner, user_details, get_all_members, is_user_creator_dm

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
        'owner' : creator_u_id,
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

def dm_details_v1(auth_user_id, dm_id):

    if not is_dm_valid(dm_id):
        raise InputError(description="Dm_id does not refer to a valid dm")
    
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description="User not exist in this dm")
        
    dm_owner_id = get_dm_owner(dm_id)

    all_members_id_list = get_all_user_id_dm(dm_id)

    return {
        'name': get_dm_name(dm_id),
        'owner': user_details([dm_owner_id]),
        'all_members': get_all_members(all_members_id_list)
    }
    
def dm_leave_v1(auth_user_id, dm_id):
    
    if not is_dm_valid(dm_id):
        raise InputError(description ="Dm_id does bot refer to a valid dm.")
        
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description="User not exist in this dm")

    store = data_store.get()
    dm_store= store['dms']
    
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            dm['all_members'].remove(auth_user_id)
            if dm['owner'] == auth_user_id:
                dm['owner'] = None
    data_store.set(store)
    
    return {}

def dm_remove_v1(auth_user_id, dm_id):
    
    if not is_dm_valid(dm_id):
        raise InputError(description ="Dm_id does bot refer to a valid dm.")
    if not is_user_creator_dm(auth_user_id, dm_id):
        raise AccessError(description="User is not the creator of this dm")

    store = data_store.get()
    dm_store= store['dms']

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            dm_store.remove(dm)
    data_store.set(store)
    return{}

def dm_messages_v1(auth_user_id, dm_id, start):

    if not is_dm_valid(dm_id):
        raise InputError(description ="Dm_id does bot refer to a valid dm.")

    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description="User not exist in this dm")

    if start < 0:
        raise InputError(description="Invalid Start Index")
    
    store = data_store.get()
    dm_store = store['dms']

    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            if len(dm['messages']) - 1 < start:
                return InputError(description="Invalid Start Index")

    messages_dm = dm['messages']
    messages_store = store['messages']
    returned_messages = []
    end = start + 50
    
    for idx , _ in enumerate(messages_dm):
        if start <= idx < end:
            returned_messages.append(messages_store[messages_dm[idx]]['message'])

    if len(returned_messages) - 1 < end - start:
        end = -1

    return {
        'messages': returned_messages,
        'start': start,
        'end': end,
    }


