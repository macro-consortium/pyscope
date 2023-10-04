import pytest


def test_issafe(winer_sm):
    assert winer_sm.IsSafe is not None
