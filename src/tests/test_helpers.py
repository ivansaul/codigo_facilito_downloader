import pytest

from facilito.helpers import clean_string, hashify, slugify


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello, World!", "Hello World"),
        ("   1234:;<>?{}|", "1234"),
        ("Café! Frío?", "Café Frío"),
        ("º~ª Special chars: @#$%^&*()!", "Special chars"),
    ],
)
def test_clean_string(text, expected):
    assert clean_string(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello, World!", "hello-world"),
        ("   1234:;<>?{}|", "1234"),
        ("Café! Frío?", "cafe-frio"),
        ("º~ª Special chars: @#$%^&*()!", "special-chars"),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Hello, World!",
            "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f",
        ),
        (
            "Hello, World!",
            "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f",
        ),
    ],
)
def test_hashify(text, expected):
    assert hashify(text) == expected
