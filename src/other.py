import re
from src.data_store import data_store
from src.error import InputError

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['passwords'] = []
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
    

def check_email_validity(email):
    """ Checks if email is a valid input and raises an error if it isn't.

    Arguments:
        email(string)     - The email of the user to be registered.

    Exceptions:
        InputError - Occurs when  email does not match a valid email length or pattern.
            
    Return Value:
        None
    """
    max_len_email_user_char = 64
    max_len_email_domain_char = 64
    max_len_email_path_char = 256
    if None == re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',email):
        raise InputError("Invalid Email")
    
    #https://stackoverflow.com/questions/45082170/regex-to-split-the-email-address-in-python
    email_list = re.findall(r'(.+)@(.+)\.(.+)', email)

    if len(email_list[0][0]) > max_len_email_user_char or len(email_list[0][1]) > max_len_email_domain_char or len(email_list[0][2]) > max_len_email_path_char:
        raise InputError("Email too long")


def check_password_validity(password):
    """ Checks if password is a valid input and raises an error if it isn't.

    Arguments:
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError - Occurs when  password does not match a valid password length.
                    

    Return Value:
        None
    """
    min_password_len = 6
    max_password_len = 128 
    if len(password) < min_password_len:
        raise InputError("Password too short!")

    if len(password) > max_password_len:
        raise InputError("Password too long!")



def search_email_password_match(email,password):
    """ Checks if valid email password combination matches register user and returns auth_user_id.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError - Occurs when  input does not match a valid password email combination.
                    

    Return Value:
        Returns { auth_user_id } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    count = 0
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
    

def search_duplicate_email(email):
    """ Searches for duplicate emails and returns a count of the number of matching emails to 
        the provided email input.

    Arguments:
        email (string)        - The email of the user to be registered.


    Exceptions:
            None 

    Return Value:
        Returns { count } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    count = 0
    for Object in users:
        if Object['email'] == email:
            count += 1
    return count


def search_handle(name_first,name_last):
    """ Searches for existing handles and appends a number as a string to create a unique and 
        valid handle.

    Arguments:
        name_first (string)   - The first name of the user to be registered.
        name_last (string)    - The last name of the user to be registered.

    Exceptions:
            None 

    Return Value:
        Returns { valid_handle } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    len_trunc = 20
    count = 0
    str_handle = ((name_first + name_last)[0:len_trunc]).lower()
    if users:
        for idx,Object in enumerate(users):
            print(Object)
            if Object['handle_str'] == str_handle:
                idx = 0
                str_handle = str_handle + str(count)
                count += 1

    valid_handle = str_handle        
    return valid_handle