import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    '''
    Clears the server data and creates a user
    '''
    user = []
    requests.delete(config.url + 'clear/v1')
    creater = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'heemail@gmail.com',
        'password' : 'he123!@#',
        'name_first' : 'Hayden',
        'name_last' : 'Everest'
    })
    user.append(json.loads(creater.text))
    member1 = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'jsemail1@gmail.com',
        'password' : 'js123!@#',
        'name_first' : 'John',
        'name_last' : 'Smith'
    })
    user.append(json.loads(member1.text))
    
    member2 = requests.post(config.url + f"auth/register/v2", json={
        'email' : 'lhemail1@gmail.com',
        'password' : 'lh123!@#',
        'name_first' : 'Lewis',
        'name_last' : 'Hamilton'
    })
    user.append(json.loads(member2.text))
    return user

def test_valid_list(setup):
    users = setup
    dm1 = requests.post(config.url + 'dm/create/v1', json={'token': users[0]['token'], 'u_ids': [users[1]['auth_user_id']]})
    dm2 = requests.post(config.url + 'dm/create/v1', json={'token': users[0]['token'], 'u_ids': [users[1]['auth_user_id'],users[2]['auth_user_id']]})

    list1 = requests.get(config.url + 'dm/list/v1', params={'token': users[0]['token']})
    assert json.loads(list1.text) == {'dms': [{'dm_id': json.loads(dm1.text)['dm_id'], 'name': 'haydeneverest, johnsmith'},
                                        {'dm_id': json.loads(dm2.text)['dm_id'], 'name': 'haydeneverest, johnsmith, lewishamilton'}
                                        ]}
                
    list2 = requests.get(config.url + 'dm/list/v1', params={'token': users[1]['token']})
    assert json.loads(list2.text) == {'dms': [{'dm_id': json.loads(dm1.text)['dm_id'], 'name': 'haydeneverest, johnsmith'},
                                        {'dm_id': json.loads(dm2.text)['dm_id'], 'name': 'haydeneverest, johnsmith, lewishamilton'}]}

    list3 = requests.get(config.url + 'dm/list/v1', params={'token': users[2]['token']})
    assert json.loads(list3.text) == {'dms': [{'dm_id': json.loads(dm2.text)['dm_id'], 'name': 'haydeneverest, johnsmith, lewishamilton'}]}

def test_bad_token(setup):
    _ = setup
    dm1 = requests.get(config.url + 'dm/list/v1', params={'token': ""})
    assert dm1.status_code == 403