"""
    I do tests somehow eventually
"""

import pytest


@pytest.fixture
def tdam_app():
    from tdam.tdam import DevApp
    app = DevApp()
    return
