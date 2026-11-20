"""Tests for the vRecur.byhour accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vNonNegativeInt


def test_byhour_returns_empty_tuple_when_absent():
    """BYHOUR is not set at all."""
    assert vRecur.from_ical("FREQ=DAILY").byhour == ()


def test_byhour_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["DAILY"], BYHOUR=[])
    assert recur.byhour == ()


def test_byhour_returns_single_value():
    assert vRecur.from_ical("FREQ=DAILY;BYHOUR=9").byhour == (9,)


def test_byhour_returns_multiple_values():
    assert vRecur.from_ical("FREQ=DAILY;BYHOUR=9,12,18").byhour == (9, 12, 18)


def test_byhour_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=DAILY;BYHOUR=0").byhour == (0,)
    assert vRecur.from_ical("FREQ=DAILY;BYHOUR=23").byhour == (23,)


def test_setting_byhour_with_single_int():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.byhour = 9
    assert recur.byhour == (9,)
    assert isinstance(recur["BYHOUR"][0], vNonNegativeInt)
    assert recur.to_ical() == b"FREQ=DAILY;BYHOUR=9"


def test_setting_byhour_with_list():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.byhour = [9, 18]
    assert recur.byhour == (9, 18)
    assert recur.to_ical() == b"FREQ=DAILY;BYHOUR=9,18"


def test_setting_byhour_with_tuple():
    recur = vRecur.from_ical("FREQ=DAILY")
    recur.byhour = (0, 12, 23)
    assert recur.byhour == (0, 12, 23)
    assert recur.to_ical() == b"FREQ=DAILY;BYHOUR=0,12,23"


def test_setting_byhour_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=DAILY;BYHOUR=9")
    recur.byhour = None
    assert recur.byhour == ()
    assert "BYHOUR" not in recur


def test_setting_byhour_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=DAILY;BYHOUR=9")
    recur.byhour = []
    assert recur.byhour == ()
    assert "BYHOUR" not in recur

    recur.byhour = [9]
    recur.byhour = ()
    assert recur.byhour == ()
    assert "BYHOUR" not in recur


def test_deleting_byhour_removes_value():
    recur = vRecur.from_ical("FREQ=DAILY;BYHOUR=9")
    del recur.byhour
    assert recur.byhour == ()
    assert "BYHOUR" not in recur


def test_deleting_byhour_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=DAILY")
    del recur.byhour
    assert recur.byhour == ()


def test_setting_byhour_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.byhour = "9"
    with pytest.raises(TypeError):
        recur.byhour = [9, "12"]


def test_setting_byhour_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(TypeError):
        recur.byhour = True
    with pytest.raises(TypeError):
        recur.byhour = [9, True]


@pytest.mark.parametrize("invalid_hour", [-1, 24, 100])
def test_setting_byhour_out_of_range_raises_invalid_calendar(invalid_hour):
    recur = vRecur.from_ical("FREQ=DAILY")
    with pytest.raises(InvalidCalendar, match="BYHOUR values must be between 0 and 23"):
        recur.byhour = invalid_hour
    with pytest.raises(InvalidCalendar, match="BYHOUR values must be between 0 and 23"):
        recur.byhour = [9, invalid_hour]


@pytest.mark.parametrize("stored", [-1, 24, "abc", True])
def test_directly_assigned_invalid_byhour_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=DAILY")
    recur["BYHOUR"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.byhour


def test_byhour_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=DAILY;BYHOUR=8,14,20")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.byhour == (8, 14, 20)
