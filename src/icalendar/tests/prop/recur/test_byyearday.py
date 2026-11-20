"""Tests for the vRecur.byyearday accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vInt


def test_byyearday_returns_empty_tuple_when_absent():
    """BYYEARDAY is not set at all."""
    assert vRecur.from_ical("FREQ=YEARLY").byyearday == ()


def test_byyearday_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["YEARLY"], BYYEARDAY=[])
    assert recur.byyearday == ()


def test_byyearday_returns_single_value():
    assert vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=100").byyearday == (100,)


def test_byyearday_returns_multiple_values():
    assert vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=1,100,300").byyearday == (
        1,
        100,
        300,
    )


def test_byyearday_negative_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=-1,-366").byyearday == (
        -1,
        -366,
    )


def test_byyearday_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=-366,-1,1,366").byyearday == (
        -366,
        -1,
        1,
        366,
    )


def test_setting_byyearday_with_single_int():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byyearday = 100
    assert recur.byyearday == (100,)
    assert isinstance(recur["BYYEARDAY"][0], vInt)
    assert recur.to_ical() == b"FREQ=YEARLY;BYYEARDAY=100"


def test_setting_byyearday_with_negative_int():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byyearday = -1
    assert recur.byyearday == (-1,)
    assert recur.to_ical() == b"FREQ=YEARLY;BYYEARDAY=-1"


def test_setting_byyearday_with_list():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byyearday = [1, -1, 366]
    assert recur.byyearday == (1, -1, 366)
    assert recur.to_ical() == b"FREQ=YEARLY;BYYEARDAY=1,-1,366"


def test_setting_byyearday_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=100")
    recur.byyearday = None
    assert recur.byyearday == ()
    assert "BYYEARDAY" not in recur


def test_setting_byyearday_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=100")
    recur.byyearday = []
    assert recur.byyearday == ()
    assert "BYYEARDAY" not in recur

    recur.byyearday = [100]
    recur.byyearday = ()
    assert recur.byyearday == ()
    assert "BYYEARDAY" not in recur


def test_deleting_byyearday_removes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=100")
    del recur.byyearday
    assert recur.byyearday == ()
    assert "BYYEARDAY" not in recur


def test_deleting_byyearday_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.byyearday
    assert recur.byyearday == ()


def test_setting_byyearday_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.byyearday = "100"
    with pytest.raises(TypeError):
        recur.byyearday = [1, "100"]


def test_setting_byyearday_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.byyearday = True
    with pytest.raises(TypeError):
        recur.byyearday = [1, True]


def test_setting_byyearday_to_zero_raises_invalid_calendar():
    """RFC 5545 Section 3.3.10 explicitly states the value 0 MUST NOT be used."""
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYYEARDAY values must be between -366 and -1 or 1 and 366",
    ):
        recur.byyearday = 0


@pytest.mark.parametrize("invalid_day", [-367, 0, 367, 500])
def test_setting_byyearday_out_of_range_raises_invalid_calendar(invalid_day):
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYYEARDAY values must be between -366 and -1 or 1 and 366",
    ):
        recur.byyearday = invalid_day
    with pytest.raises(
        InvalidCalendar,
        match="BYYEARDAY values must be between -366 and -1 or 1 and 366",
    ):
        recur.byyearday = [1, invalid_day]


@pytest.mark.parametrize("stored", [-367, 0, 367, "abc", True])
def test_directly_assigned_invalid_byyearday_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["BYYEARDAY"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.byyearday


def test_byyearday_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=YEARLY;BYYEARDAY=1,-1,366")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.byyearday == (1, -1, 366)
