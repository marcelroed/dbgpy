import torch

from dbgpy import dbg, config

config.prefix_format = "{path}:"

dbg(config.prefix_format)

def test_literal_string():
    print()
    dbg("This is a test string")


def test_expression_string():
    print()
    # Using addition means the expression will be printed
    dbg("This is a test string" + " and another string" + f" some formatting {20:.2f}")
    # Formatted strings are printed directly without the expression
    dbg(f"This is just a formatted string with {20:.2f}")


def test_expression():
    print()
    dbg(100 + 56 + 13)


def test_multiple_expressions():
    print()
    x = 100
    dbg(100 + 56 + 13, 15 + 32, x)


def test_multiple_expressions_mixed():
    print()
    x = 20
    dbg(x, "a test string", 100 + 56 + 13, 15 + 32)


def test_multiline_expression():
    print()
    dbg((1 + 3 + 5))


def test_multiline_string():
    print()
    dbg(
        "This is a test string\n"
        "This is a test string\n"
        "and another string\n"
        f"some formatting {20:.2f}",
        torch.randn(3, 3).T,
    )

