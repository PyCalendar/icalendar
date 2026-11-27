"""Tests for the vRecur.byminute accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vNonNegativeInt


def test_byminute_returns_empty_tuple_when_absent():
    """BYMINUTE is not set at all."""
    assert vRecur.from_ical("FREQ=HOURLY").byminute == ()


def test_byminute_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["HOURLY"], BYMINUTE=[])
    assert recur.byminute == ()


def test_byminute_returns_single_value():
    assert vRecur.from_ical("FREQ=HOURLY;BYMINUTE=30").byminute == (30,)


def test_byminute_returns_multiple_values():
    assert vRecur.from_ical("FREQ=HOURLY;BYMINUTE=0,15,30,45").byminute == (
        0,
        15,
        30,
        45,
    )


def test_byminute_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=HOURLY;BYMINUTE=0").byminute == (0,)
    assert vRecur.from_ical("FREQ=HOURLY;BYMINUTE=59").byminute == (59,)


def test_setting_byminute_with_single_int():
    recur = vRecur.from_ical("FREQ=HOURLY")
    recur.byminute = 15
    assert recur.byminute == (15,)
    assert isinstance(recur["BYMINUTE"][0], vNonNegativeInt)
    assert recur.to_ical() == b"FREQ=HOURLY;BYMINUTE=15"


def test_setting_byminute_with_list():
    recur = vRecur.from_ical("FREQ=HOURLY")
    recur.byminute = [0, 30]
    assert recur.byminute == (0, 30)
    assert recur.to_ical() == b"FREQ=HOURLY;BYMINUTE=0,30"


def test_setting_byminute_with_tuple():
    recur = vRecur.from_ical("FREQ=HOURLY")
    recur.byminute = (10, 20, 59)
    assert recur.byminute == (10, 20, 59)
    assert recur.to_ical() == b"FREQ=HOURLY;BYMINUTE=10,20,59"


def test_setting_byminute_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=HOURLY;BYMINUTE=30")
    recur.byminute = None
    assert recur.byminute == ()
    assert "BYMINUTE" not in recur


def test_setting_byminute_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=HOURLY;BYMINUTE=30")
    recur.byminute = []
    assert recur.byminute == ()
    assert "BYMINUTE" not in recur

    recur.byminute = [30]
    recur.byminute = ()
    assert recur.byminute == ()
    assert "BYMINUTE" not in recur


def test_deleting_byminute_removes_value():
    recur = vRecur.from_ical("FREQ=HOURLY;BYMINUTE=30")
    del recur.byminute
    assert recur.byminute == ()
    assert "BYMINUTE" not in recur


def test_deleting_byminute_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=HOURLY")
    del recur.byminute
    assert recur.byminute == ()


def test_setting_byminute_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=HOURLY")
    with pytest.raises(TypeError):
        recur.byminute = "30"
    with pytest.raises(TypeError):
        recur.byminute = [0, "30"]


def test_setting_byminute_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=HOURLY")
    with pytest.raises(TypeError):
        recur.byminute = True
    with pytest.raises(TypeError):
        recur.byminute = [0, True]


@pytest.mark.parametrize("invalid_minute", [-1, 60, 100])
def test_setting_byminute_out_of_range_raises_invalid_calendar(invalid_minute):
    recur = vRecur.from_ical("FREQ=HOURLY")
    with pytest.raises(
        InvalidCalendar, match="BYMINUTE values must be between 0 and 59"
    ):
        recur.byminute = invalid_minute
    with pytest.raises(
        InvalidCalendar, match="BYMINUTE values must be between 0 and 59"
    ):
        recur.byminute = [0, invalid_minute]


@pytest.mark.parametrize("stored", [-1, 60, "abc", True])
def test_directly_assigned_invalid_byminute_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=HOURLY")
    recur["BYMINUTE"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.byminute


def test_byminute_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=HOURLY;BYMINUTE=0,15,30,45")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.byminute == (0, 15, 30, 45)
