"""example tests

e.g. for "words"
"""
import template


def test_throws():
    out = template.words("in this", "string")
    assert out == ["in", "this", "string"]
