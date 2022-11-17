"""example tests

e.g. for "words"
"""
import template


def test_words():
    out = template.words("in this", "string")
    assert out == ["in", "this", "string"]
