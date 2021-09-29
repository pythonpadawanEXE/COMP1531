from src import auth
import re
import pytest
from src.data_store import data_store
from src.error import InputError
from src import other
'''
Valid Email Tests
'''
#r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"

def test_valid_email_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

'''
Invalid Email Tests
'''
#r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"

def test_invalid_email_1():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('invalidemailgmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_invalid_email_too_long_1():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('invalidemailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong@gmail.com', '123abc!@#', 'Hayden', 'Everest')

def test_invalid_email_too_long_2():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('invalidemail@gmailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong.com', '123abc!@#', 'Hayden', 'Everest')

def test_invalid_email_too_long_3():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('invalidemailgmail.comloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', '123abc!@#', 'Hayden', 'Everest')

'''
Invalid Email address is already being used by another user
'''
def test_duplicate_email():
    other.clear_v1()
    result = auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest') # Expect fail since we already registered



'''
Valid Multiple Registrations with unique emails
'''
def test_multiple_emails():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Bake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Cake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert result2['auth_user_id'] - result1['auth_user_id'] == 1
    assert result3['auth_user_id'] - result2['auth_user_id'] == 1

'''
Valid Multiple Registrations with unique lowercase handles
'''
def test_multiple_emails_valid_handles():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert result2['auth_user_id'] - result1['auth_user_id'] == 1
    assert result3['auth_user_id'] - result2['auth_user_id'] == 1
    #TODO: then assert datastore to check all contained handles are unique and in lower case
    #https://stackoverflow.com/questions/11092511/python-list-of-unique-dictionaries
    #Will likely need to debug below code
    store = data_store.get()
    users = store['users']
    DistinctUsers = list({Object['handle_str']:Object for Object in users}.values())
    # print(users)
    # print(DistinctUsers)
    assert len(users) == len(DistinctUsers)
'''
data = {
    'users': [
        {
            'u_id': 1,
            'email' : 'jake@gmail.com',
            'name_first' : 'Jake',
            'name_last'  : 'Edwards',
            'handle_str' : 'jakeedwards'

        },
        {
            'u_id': 2,
            'email' : 'jake2@gmail.com',
            'name_first' : 'Jake',
            'name_last'  : 'Edwards',
            'handle_str' : 'jakeedwards0'
        }
    ],

    'passwords' : [
        {
            'u_id':1,
            'password' : 'Password',
        }
        {
            'u_id':2,
            'password' : 'Password',
        }

    ]

'''

'''
Invalid length of password is less than 6 characters
'''
def test_invalid_short_password():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail1@gmail.com', 'short', 'Hayden', 'Everest')
'''
Invalid length of password is more than 256 characters
'''
def test_invalid_long_password():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail2@gmail.com', 'loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', 'Hayden', 'Everest')
'''
Valid length of password is more than 6 characters
'''
def test_valid_len_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail3@gmail.com', 'nottooshort', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
'''
Since str_handle must be letters or hyphens (a-z0-9)
'''
def test_valid_name_first():
    other.clear_v1()

    result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', 'Jake-Allan', 'Edwards')
    assert isinstance(result['auth_user_id'],int)


def test_invalid_name_first_1():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', 'Jake@Allan', 'Edwards')

def test_invalid_name_first_2():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', '------', 'Edwards')






def test_valid_name_last():
    other.clear_v1()

    result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', 'Jake', 'Allan-Edwards')
    assert isinstance(result['auth_user_id'],int)

def test_invalid_name_last():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', 'Jake@Allan', '-----')

def test_invalid_name_last():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', 'Jake', 'Allan@Edwards')
    

'''
Invalid length of name_first is not between 1 and 50 characters inclusive
'''

def test_name_first_invalid_length_short():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail4@gmail.com', '123ab78', '', 'Lastname')

def test_name_first_invalid_length_long():
    other.clear_v1()
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail5@gmail.com', '123ab78', str_name, 'Lastname')
'''
Valid length of name_first is  between 1 and 50 characters inclusive
'''
def test_name_first_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail6@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)

def test_name_first_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail7@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)
'''
Invalid length of name_last is not between 1 and 50 characters inclusive
'''
def test_name_last_invalid_length_short():
    other.clear_v1()
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail8@gmail.com', '123ab78', 'Firstname', '')

def test_name_last_invalid_length_long():
    other.clear_v1()
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail9@gmail.com', '123ab78', 'Firstname', str_name)

'''
Valid length of name_last is  between 1 and 50 characters inclusive
'''
def test_name_last_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail10@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)

def test_name_last_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail11@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)


'''
Test Max Users Assumption

'''
def test_valid_max_users_registration():
    other.clear_v1()
    for i in range(2000):
        str_name = 'John' + f'{i}'
        result = auth.auth_register_v1('validemail10'+f'{i}'+ '@gmail.com', '123ab78', 'Firstname', str_name)
        assert isinstance(result['auth_user_id'],int)


#     PASSWORD FUTURE WARNINGS
# =================================
#???