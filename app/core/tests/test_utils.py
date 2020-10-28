from unittest.mock import MagicMock

from core.utils import recursive_getattr


def test_recursive_getattr():
    initial = MagicMock()
    initial.a = 1
    initial.b.c = 2
    initial.c.d.e = 3

    paths = [
        ["a", 1],
        ["b.c", 2],
        ["c.d.e", 3],
    ]

    for path, result in paths:
        assert recursive_getattr(initial, path) == result
