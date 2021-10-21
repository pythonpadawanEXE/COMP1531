import re
from src.data_store import data_store
from src.error import InputError,AccessError
import hashlib
import jwt

SESSION_TRACKER = 0
SECRET = 'COMP1531'

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['passwords'] = []
    store['permissions'] = []
    store['dms'] = []
    store['messages'] = []
    data_store.set(store)
    return {}

# Check if the channel with channel_id is valid
def is_channel_valid(channel_id):

    channel_valid = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if channel_id == chan['id']:
            channel_valid = True

    return channel_valid

# Checks if user with auth_user_id is in channel with channel_id
def is_user_authorised(auth_user_id, channel_id):
    is_authorised = False
    store = data_store.get()
    channel_store = store['channels']
    print(f"channel_store_authroised {channel_store}")
    print(f"auth_user_id {auth_user_id} channel_id {channel_id}")
    for chan in channel_store:
        if auth_user_id in chan['all_members']:
            is_authorised = True

    return is_authorised

# Returns the name of the channel with channel_id
def get_channel_name(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['name']

# Checks if channel with channel_id is public or private
def is_channel_public(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['is_public']

# Returns the auth_user_id of the channel owner with ID channel_id
def get_channel_owner(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['owner_members'][0]

# Reurns a list containing details of the owner members
def user_details(auth_user_id):
    user_details_list = []
    store = data_store.get()
    user_store = store['users']

    for user in user_store:
        if user['u_id'] == auth_user_id:
            user_details_list.append(user)
    return user_details_list

# Returns a list of all the auth_user_id of a channel
def get_all_user_id_channel(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['all_members']

# Returns a list of all members and associated details corresponding to their u_id in auth_id_list
def get_all_members(auth_id_list):
    all_members_list = []
    store = data_store.get()
    user_store = store['users']

    for auth_id in auth_id_list:
        for user in user_store:
            if auth_id == user['u_id']:
                all_members_list.append(user)

    return all_members_list

def verify_user_id(auth_user_id):
    """ Helper function that verifies that the user exists in the data store,
        if in data store returns true else false.

        Arguments:
            auth_user_id (int)    - The user id of the user being verified.

        Return Value:
            Returns True on user id being found.
            Returns False on user id not being found.
    """
    is_authorised = False
    store = data_store.get()

    user_store = store['users']
    for user in user_store:
        if user['u_id'] == auth_user_id:
            is_authorised = True
    return is_authorised
    
'''
check email validity
'''
def check_email_validity(email):
    max_len_email_user_char = 64
    max_len_email_domain_char = 64
    max_len_email_path_char = 256
    if None == re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',email):
        raise InputError("Invalid Email")
    
    #https://stackoverflow.com/questions/45082170/regex-to-split-the-email-address-in-python
    email_list = re.findall(r'(.+)@(.+)\.(.+)', email)

    if len(email_list[0][0]) > max_len_email_user_char or len(email_list[0][1]) > max_len_email_domain_char or len(email_list[0][2]) > max_len_email_path_char:
        raise InputError("Email too long")

'''
check password validity
'''
def check_password_validity(password):
    min_password_len = 6
    max_password_len = 128 
    if len(password) < min_password_len:
        raise InputError("Password too short!")

    if len(password) > max_password_len:
        raise InputError("Password too long!")


'''
checks login credidentials match registered user 
'''
def search_email_password_match(email,password):
    store = data_store.get()
    users = store['users']
    password = hash(password)
    id = None
    for Object in users:
        if Object['email'] == email:
            id = Object['u_id']
            break
    if id == None:
        raise InputError("No User exists with this email/password combination")

    passwords = store['passwords']
    for Object in passwords:
        if Object['u_id'] == id and Object['password'] == password :
            return {
                'auth_user_id': id,
            }
    raise InputError("No User exists with this email/password combination")
    
'''
searches for duplicate emails and return a count of matching emails to the provided input
'''
def search_duplicate_email(email):
    store = data_store.get()
    users = store['users']
    count = 0
    for Object in users:
        if Object['email'] == email:
            count += 1
    return count
'''
Search for Handle given auth user id
'''
def search_handle(auth_user_id):
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['u_id'] == auth_user_id:
            return user['handle_str']
    return None
'''
Searches for existing handles and appends a number as a string to create a unique and valid handle
'''
def make_handle(name_first,name_last):
    store = data_store.get()
    users = store['users']
    print(f"handle: {users}")
    len_trunc = 20
    count = 0
    #make lowercase then remove non-alphanumeric characters
    name_first = name_first.lower()
    name_first = ''.join(ch for ch in name_first if ch.isalnum())
    #make lowercase then remove non-alphanumeric characters
    name_last = name_last.lower()
    name_last = ''.join(ch for ch in name_last if ch.isalnum())

    #If the concatenation is longer than 20 characters, it is cut off at 20 characters
    str_handle = ((name_first + name_last)[0:len_trunc])
    #if handle is taken append
    valid_handle = None
    if users:
        for user in users:
            if user['handle_str'] == str_handle:
                valid_handle = str_handle + str(count)
                count += 1
            elif user['handle_str'] == valid_handle:
                valid_handle = str_handle + str(count)
                count += 1
    if valid_handle is None:
        valid_handle = str_handle
    return valid_handle

def is_global_owner(auth_user_id):
    # Returns true if the given user is the global owner (first registered user).
    user_store = data_store.get()["users"]
    for user in user_store:
        if auth_user_id == user['u_id']:
            if user['permission_id'] == 1:
                return True
            else:
                return False
    return False

# def make_token(auth_user_id,session_id):
#     '''
    
#     Makes a  new JWT. 

#     Arguments:
#         auth_user_id (int) - Unique ID of authorised user
#         session_id (int) - Unique ID of Session
#     Return Value:   
#         token (string) on Successful completion.
#     '''
#     return generate_jwt(auth_user_id, session_id)

def return_token(auth_user_id):
    '''
    
    Return a  valid JWT given valid login credidentials.

    Arguments:
        auth_user_id          - auth_user_id (int) - Unique ID of authorised user
        
    Return Value:   
        token (string) on Successful completion.
    '''
    session_id = generate_new_session_id()
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['u_id'] == auth_user_id:
            user['sessions'].append(session_id)
    data_store.set(store)
    return  generate_jwt(auth_user_id, session_id)

def check_valid_token(token):
    '''
    
    Return a  boolean value for the validity of the token.

    Arguments:
       token (string)        - The token of the user session
       
        
    Return Value:   
        {'auth_user_id':decoded_token['auth_user_id'],
        'session_id':decoded_token['session_id']} on valid token.
        None on Invalid Token
    '''
    if None == re.fullmatch(r'^[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*$',token):
        raise AccessError(description="Invalid Token")
    decoded_token = decode_jwt(token)
    if isinstance(decoded_token,dict) == False:
        raise AccessError(description="Invalid Token")

    store = data_store.get()
    users = store['users']
    
    for user in users:
        if user['u_id'] == decoded_token['auth_user_id']:
            for session_id in user['sessions']:
                if session_id == decoded_token['session_id']:
                    return {'auth_user_id':decoded_token['auth_user_id'],'session_id':decoded_token['session_id']}
    raise AccessError(description="Invalid Token")
    



def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def hash(input_string):
    """Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def generate_jwt(auth_user_id, session_id=None):
    """Generates a JWT using the global SECRET

    Args:
        auth_user_id ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """
    if session_id is None:
        session_id = generate_new_session_id()
    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the decoded JWT dict
    """
    try :
        decoded_token = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    except Exception as decode_problem:
        raise AccessError("Invalid Token") from decode_problem

    return decoded_token

def is_user_in_dm(auth_user_id, dm_id):
    """
    Check if a user is a member of a dm
    Args:
        auth_user_id (int)  - Unique authenticated user id.
        dm_id   (int)       - Unique direct message id.

        return boolean
    """
    is_user_in_dm = False
    store = data_store.get()
    dms = store['dms']
    for dm in dms:
        if dm['dm_id'] == dm_id and auth_user_id in dm['all_members']:
            is_user_in_dm = True
    return is_user_in_dm

def generate_dm_name(all_members):
    store = data_store.get()
    users = store['users']
    name_list = []
    for member in all_members:
        for user in users:
            if member == user['u_id']:
                name_list.append(user['handle_str'])
    name = ', '.join(sorted(name_list))
    return name
    
