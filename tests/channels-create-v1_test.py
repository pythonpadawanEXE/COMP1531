# channels-create_test.py
# pytest file to test the implementation of channels_create_v1

import pytest

def test_channels_create_v1_simple():
    new_channel = channels_create_v1()
    assert(new_channel['channel_id'] == 1)