from src import other
import pytest
from src.data_store import data_store
import requests
from src import config

BASE_URL = config.url

def test_clear_v1_check_store():
    other.clear_v1()
    store = data_store.get()
    messages = []
        # replace assertions by conditions
    if not store['users']:
        messages.append("Users is  empty")
    if not store['channels']:
        messages.append("Channels is  empty")

    if not store['passwords']:
        messages.append("Passwords is  empty")

    # assert no error message has been registered, else print messages
    assert len(messages) == 3, "actions occured:\n{}".format("\n".join(messages))


def test_clear_v1():
    assert other.clear_v1() == {}


def test_clear_v1_endpoint():
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    assert response.json() == {}

