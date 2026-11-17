import re

import pytest

from icalendar.prop.float import vFloat


def test_zero():
    assert vFloat(0.0).to_ical() == b"0.0"


def test_roundtrip():
    assert vFloat.from_ical(vFloat("42.0").to_ical()) == 42.0
    assert vFloat.from_ical("42.0") == 42.0


def test_error():
    """Error: not an float string"""
    with pytest.raises(ValueError):
        vFloat.from_ical("not a float")


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "infinity", "1e999"])
def test_reject_non_finite(value):
    """Non-finite floats are not valid FLOAT values per RFC 5545."""
    with pytest.raises(ValueError):
        vFloat.from_ical(value)


def test_ical_value():
    """ical_value property returns the float value."""
    assert vFloat(1.0).ical_value == 1.0
    assert vFloat(0.0).ical_value == 0.0


RFC5545_FLOAT = re.compile(rb"^[+-]?\d+(?:\.\d+)?$")
"""FLOAT of RFC 5545 3.3.7: no exponent, optional sign, optional fraction."""


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1e-5, b"0.00001"),
        (-2e-5, b"-0.00002"),
        (1e-7, b"0.0000001"),
        (1e16, b"10000000000000000"),
        (-1e16, b"-10000000000000000"),
        (1.333, b"1.333"),
        (37.386013, b"37.386013"),
        (0.0, b"0.0"),
        (42.0, b"42.0"),
    ],
)
def test_no_exponent(value, expected):
    """FLOAT carries no exponent, see RFC 5545 3.3.7."""
    ical = vFloat(value).to_ical()
    assert ical == expected
    assert RFC5545_FLOAT.match(ical), ical


def test_small_value_keeps_its_precision():
    """A value far below 1e-04 must not be rounded away when formatted."""
    assert vFloat(1e-7).to_ical() == b"0.0000001"
    assert vFloat.from_ical("0.0000001") == 1e-7


def test_written_value_parses_back():
    for value in (1e-5, -2e-5, 1e16, 37.386013):
        assert vFloat.from_ical(vFloat(value).to_ical().decode()) == value
