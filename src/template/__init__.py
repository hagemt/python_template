"""utility functions

e.g. words("I say") => ["I", "say"]
"""
import re
import typing as T


def words(*args) -> T.List[str]:
    text = " ".join(args)
    return [t for t in re.findall(r"\w+|\W+", text) if t.strip()]
