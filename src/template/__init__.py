"""utility functions

e.g. words("I say") => ["I", "say"]
"""
import typing as T


def words(*args, space=" ", **kwargs) -> T.List[str]:
    return space.join(args).split(**kwargs)
