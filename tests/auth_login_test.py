from src import auth
import re
import pytest
from src.data_store import data_store
from src.error import InputError
from src import other

#test for standard login
def test_valid_login_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

#multiple  register and one login
def test_valid_login_multi_registered():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#1', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#2', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail3@gmail.com', '123abc!@#3', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#4', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

#multiple logins register and login are using the same password
def test_valid_login_multi_registered_same_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail3@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

#multiple logins register and login are  sequential operations
def test_multiple_logins_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail1@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail2@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail3@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail3@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_login_v1('validemail4@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

#multiple logins register and login are not sequential operations
def test_multiple_logins_2():
    other.clear_v1()
    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_login_v1('validemail4@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_login_v1('validemail2@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

    result = auth.auth_login_v1('validemail1@gmail.com', '123abc!@#')
    assert isinstance(result['auth_user_id'],int)

#email login doesnt match a registered user
def test_invalid_login_email():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    with pytest.raises(InputError):
        result = auth.auth_login_v1('validemailgmail.com', '123abc!@#')



#login password doesnt match registered password
def test_invalid_login_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    with pytest.raises(InputError):
        result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#?')

#login password doesnt match registered password with multiple registrations
def test_invalid_login_password_multi_registered():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#1', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#2', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail3@gmail.com', '123abc!@#3', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#4', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    with pytest.raises(InputError):
        result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#?')

#login password doesnt match registered password with multiple registrations with same password
def test_invalid_login_password_multi_registered_same_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail1@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail2@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail3@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    result = auth.auth_register_v1('validemail4@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    with pytest.raises(InputError):
        result = auth.auth_login_v1('validemail@gmail.com', '123abc!@#?')

def test_valid_max_users_registration():
    other.clear_v1()
    for i in range(2000):
        str_name = 'John' + f'{i}'
        result = auth.auth_register_v1('validemail10'+f'{i}'+ '@gmail.com', '123ab78', 'Firstname', str_name)
        assert isinstance(result['auth_user_id'],int)

    for i in range(2000):
        str_name = 'John' + f'{i}'
        result = auth.auth_login_v1('validemail10'+f'{i}'+ '@gmail.com', '123ab78')
        assert isinstance(result['auth_user_id'],int)