from src.data_store import data_store
from src.error import InputError
import re

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
    count = 0
    id = None
    for Object in users:
        if Object['email'] == email:
            id = Object['u_id']
            break
    if id == None:
        raise InputError("No User exists with this email/password combination")
        return

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
Searches for existing handles and appends a number as a string to create a unique and valid handle
'''
def search_handle(name_first,name_last):
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

'''
login user provde either 'auth_user_id': id or raise an input error
'''

def auth_login_v1(email, password):
 
    check_email_validity(email)
    check_password_validity(password)
    
    return search_email_password_match(email,password)

'''
create a unique user dictionary in the users data store with the provided inputs and creates a unique handle and id
'''
def auth_register_v1(email, password, name_first, name_last):
    max_name_len = 50
    min_name_len = 1
   

    if search_duplicate_email(email) != 0:
        raise InputError("Duplicate Email")

    check_email_validity(email)
    check_password_validity(password)
    
    #check valid input for name_last i.e. cant be only number or hyphens cannot contain symbols must contain letters
    if not (len(re.findall(r'[A-Za-z]',name_last)) + len(re.findall(r'[\s\-0-9]',name_last)) == len(name_last) and len(re.findall(r'[A-Za-z]',name_last)) > 0):
        raise InputError("name_last invalid character sequence, sequence must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")

    if len(name_last) > max_name_len or len(name_last) < min_name_len:
        raise InputError("Invalid First Name Length")
    
    store = data_store.get()
    users = store['users']
    passwords = store['passwords']
    users.append(
         {
            'u_id': len(users) + 1,
            'email' : email,
            'name_first' : name_first,
            'name_last'  : name_last,
            'handle_str' : search_handle(name_first,name_last),

        }

    )
    passwords.append(
        {
            'u_id': len(users),
            'password': password,
        }
    )
    data_store.set(store)

    return {
        'auth_user_id': len(users),
    }
