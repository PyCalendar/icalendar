"""Tests for the vRecur.bymonthday accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vInt


def test_bymonthday_returns_empty_tuple_when_absent():
    """BYMONTHDAY is not set at all."""
    assert vRecur.from_ical("FREQ=MONTHLY").bymonthday == ()


def test_bymonthday_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["MONTHLY"], BYMONTHDAY=[])
    assert recur.bymonthday == ()


def test_bymonthday_returns_single_value():
    assert vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=15").bymonthday == (15,)


def test_bymonthday_returns_multiple_values():
    assert vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=1,15,31").bymonthday == (
        1,
        15,
        31,
    )


def test_bymonthday_negative_values_are_valid():
    assert vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=-1,-31").bymonthday == (
        -1,
        -31,
    )


def test_bymonthday_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=-31,-1,1,31").bymonthday == (
        -31,
        -1,
        1,
        31,
    )


def test_setting_bymonthday_with_single_int():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur.bymonthday = 15
    assert recur.bymonthday == (15,)
    assert recur["BYMONTHDAY"] == [vInt(15)]
    assert recur.to_ical() == b"FREQ=MONTHLY;BYMONTHDAY=15"


def test_setting_bymonthday_with_list_of_ints():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur.bymonthday = [1, 15, 31]
    assert recur.bymonthday == (1, 15, 31)
    assert recur["BYMONTHDAY"] == [vInt(1), vInt(15), vInt(31)]
    assert recur.to_ical() == b"FREQ=MONTHLY;BYMONTHDAY=1,15,31"


def test_setting_bymonthday_with_tuple_of_ints():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur.bymonthday = (5, 10, 20)
    assert recur.bymonthday == (5, 10, 20)
    assert recur["BYMONTHDAY"] == [vInt(5), vInt(10), vInt(20)]


def test_setting_bymonthday_with_negative_ints():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur.bymonthday = [-1, -15, -31]
    assert recur.bymonthday == (-1, -15, -31)
    assert recur["BYMONTHDAY"] == [vInt(-1), vInt(-15), vInt(-31)]
    assert recur.to_ical() == b"FREQ=MONTHLY;BYMONTHDAY=-1,-15,-31"


def test_setting_bymonthday_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=15")
    recur.bymonthday = None
    assert recur.bymonthday == ()
    assert "BYMONTHDAY" not in recur
    assert recur.to_ical() == b"FREQ=MONTHLY"


def test_setting_bymonthday_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=15")
    recur.bymonthday = []
    assert recur.bymonthday == ()
    assert "BYMONTHDAY" not in recur

    recur.bymonthday = [15]
    recur.bymonthday = ()
    assert recur.bymonthday == ()
    assert "BYMONTHDAY" not in recur


def test_deleting_bymonthday_removes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=15")
    del recur.bymonthday
    assert recur.bymonthday == ()
    assert "BYMONTHDAY" not in recur


def test_deleting_bymonthday_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    del recur.bymonthday
    assert recur.bymonthday == ()


def test_setting_bymonthday_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(TypeError):
        recur.bymonthday = "15"
    with pytest.raises(TypeError):
        recur.bymonthday = [1, "15"]


def test_setting_bymonthday_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(TypeError):
        recur.bymonthday = True
    with pytest.raises(TypeError):
        recur.bymonthday = [1, True]


def test_setting_bymonthday_to_zero_raises_invalid_calendar():
    """RFC 5545 Section 3.3.10 explicitly states the value 0 MUST NOT be used."""
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYMONTHDAY values must be between -31 and -1 or 1 and 31",
    ):
        recur.bymonthday = 0


@pytest.mark.parametrize("invalid_day", [-32, 0, 32, 50])
def test_setting_bymonthday_out_of_range_raises_invalid_calendar(invalid_day):
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYMONTHDAY values must be between -31 and -1 or 1 and 31",
    ):
        recur.bymonthday = invalid_day
    with pytest.raises(
        InvalidCalendar,
        match="BYMONTHDAY values must be between -31 and -1 or 1 and 31",
    ):
        recur.bymonthday = [1, invalid_day]


@pytest.mark.parametrize("stored", [-32, 0, 32, "abc", True])
def test_directly_assigned_invalid_bymonthday_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur["BYMONTHDAY"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.bymonthday


def test_bymonthday_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYMONTHDAY=1,-1,15")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.bymonthday == (1, -1, 15)
