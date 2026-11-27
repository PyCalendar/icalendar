"""Test the access to parameters via getter/setter properties."""

import pytest

from icalendar import Parameters
from icalendar.enums import VALUE


@pytest.fixture
def p():
    """Empty test property."""
    return Parameters()


def test_value_parameter_default(p):
    """Test default value."""
    assert p.value is None


def test_set_value(p):
    """Set the value, convert"""
    p.value = "test"
    assert p.value == "TEST"
    assert p["VALUE"] == "TEST"


def test_conversion(p):
    """Converted to enum."""
    p.value = "DATE-TIME"
    assert p.value == VALUE.DATE_TIME


def test_delete_value(p):
    """Delete the value."""
    p.value = "test"
    del p.value
    assert p.value is None
    assert "VALUE" not in p
    del p.value
    assert p.value is None
    assert "VALUE" not in p


def test_delete_value_None(p):
    """Delete the value."""
    p.value = "test"
    p.value = None
    assert p.value is None
    assert "VALUE" not in p
    p.value = None
    assert p.value is None
    assert "VALUE" not in p


def test_params_deprecated(p):
    """``Parameters.params()`` is deprecated in favor of ``keys()``."""
    p["CN"] = "Doe, John"
    with pytest.warns(
        DeprecationWarning,
        match="params is deprecated and will be removed in icalendar 9",
    ):
        assert list(p.params()) == list(p.keys())
