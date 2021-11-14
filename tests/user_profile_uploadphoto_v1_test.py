import sys
import urllib.request
from PIL import Image
import os
import requests
import json
from src import config

def test_invalid_token():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    requests.post(config.url + 'auth/logout/v1', json = {'token': user1["token"]})
    upload_photo_setup = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 60,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_setup)
    assert upload_photo.status_code == 403

def test_invalid_url_response():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout',
        'x_start': 0,
        'y_start': 0,
        'x_end': 60,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_url_not_jpg():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://www.cse.unsw.edu.au/~richardb/',
        'x_start': 0,
        'y_start': 0,
        'x_end': 60,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_x_end_less_than_x_start():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': 10,
        'y_start': 0,
        'x_end': 0,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_y_end_less_than_y_start():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': 0,
        'y_start': 10,
        'x_end': 60,
        'y_end': 0
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_x_start_out_of_dimension():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': -1,
        'y_start': 0,
        'x_end': 60,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_y_end_out_of_dimension():
    requests.delete(config.url + 'clear/v1')
    setup = {"email": "vincnet@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp = requests.post(config.url + 'auth/register/v2', json = setup)
    user1 = json.loads(resp.text)
    upload_photo_endpoint = {
        'token': user1["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 60,
        'y_end': 10000
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    assert upload_photo.status_code == 400

def test_valid_uploadphoto():
    requests.delete(config.url + 'clear/v1')
    setup1 = {"email": "Vincent@gmail.com", "password": "123456", "name_first": "Vincent", "name_last": "Fang"}
    resp1 = requests.post(config.url + 'auth/register/v2', json = setup1)
    user1 = json.loads(resp1.text)
    setup2 = {"email": "lewis@gmail.com", "password": "123456", "name_first": "Lewis", "name_last": "Hamilton"}
    resp2 = requests.post(config.url + 'auth/register/v2', json = setup2)
    user2 = json.loads(resp2.text)
    upload_photo_endpoint = {
        'token': user2["token"],
        'img_url': 'http://img.timeinc.net/time/50coolestweb/touts/125_arts_tout.jpg',
        'x_start': 0,
        'y_start': 0,
        'x_end': 60,
        'y_end': 60
    }
    upload_photo = requests.post(config.url + 'user/profile/uploadphoto/v1', json= upload_photo_endpoint)
    profile = requests.get(config.url + 'user/profile/v1', params = {'token': user1['token'], 'u_id': user2['auth_user_id']})
    resp_user = json.loads(profile.text)['user']
    assert resp_user['profile_img_url'] == 'http://localhost:5000/static/1_1.jpg'
    assert upload_photo.status_code == 200
