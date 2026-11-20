"""Tests for the vRecur.bysecond accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vNonNegativeInt


def test_bysecond_returns_empty_tuple_when_absent():
    """BYSECOND is not set at all."""
    assert vRecur.from_ical("FREQ=MINUTELY").bysecond == ()


def test_bysecond_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["MINUTELY"], BYSECOND=[])
    assert recur.bysecond == ()


def test_bysecond_returns_single_value():
    assert vRecur.from_ical("FREQ=MINUTELY;BYSECOND=30").bysecond == (30,)


def test_bysecond_returns_multiple_values():
    assert vRecur.from_ical("FREQ=MINUTELY;BYSECOND=0,15,30,45").bysecond == (
        0,
        15,
        30,
        45,
    )


def test_bysecond_boundary_values_are_valid():
    """RFC 5545 allows values 0 to 60 (to account for leap seconds)."""
    assert vRecur.from_ical("FREQ=MINUTELY;BYSECOND=0").bysecond == (0,)
    assert vRecur.from_ical("FREQ=MINUTELY;BYSECOND=60").bysecond == (60,)


def test_setting_bysecond_with_single_int():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    recur.bysecond = 30
    assert recur.bysecond == (30,)
    assert isinstance(recur["BYSECOND"][0], vNonNegativeInt)
    assert recur.to_ical() == b"FREQ=MINUTELY;BYSECOND=30"


def test_setting_bysecond_with_list():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    recur.bysecond = [0, 30]
    assert recur.bysecond == (0, 30)
    assert recur.to_ical() == b"FREQ=MINUTELY;BYSECOND=0,30"


def test_setting_bysecond_with_tuple():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    recur.bysecond = (0, 30, 60)
    assert recur.bysecond == (0, 30, 60)
    assert recur.to_ical() == b"FREQ=MINUTELY;BYSECOND=0,30,60"


def test_setting_bysecond_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=MINUTELY;BYSECOND=30")
    recur.bysecond = None
    assert recur.bysecond == ()
    assert "BYSECOND" not in recur


def test_setting_bysecond_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=MINUTELY;BYSECOND=30")
    recur.bysecond = []
    assert recur.bysecond == ()
    assert "BYSECOND" not in recur

    recur.bysecond = [30]
    recur.bysecond = ()
    assert recur.bysecond == ()
    assert "BYSECOND" not in recur


def test_deleting_bysecond_removes_value():
    recur = vRecur.from_ical("FREQ=MINUTELY;BYSECOND=30")
    del recur.bysecond
    assert recur.bysecond == ()
    assert "BYSECOND" not in recur


def test_deleting_bysecond_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    del recur.bysecond
    assert recur.bysecond == ()


def test_setting_bysecond_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    with pytest.raises(TypeError):
        recur.bysecond = "30"
    with pytest.raises(TypeError):
        recur.bysecond = [0, "30"]


def test_setting_bysecond_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=MINUTELY")
    with pytest.raises(TypeError):
        recur.bysecond = True
    with pytest.raises(TypeError):
        recur.bysecond = [0, True]


@pytest.mark.parametrize("invalid_second", [-1, 61, 100])
def test_setting_bysecond_out_of_range_raises_invalid_calendar(invalid_second):
    recur = vRecur.from_ical("FREQ=MINUTELY")
    with pytest.raises(
        InvalidCalendar, match="BYSECOND values must be between 0 and 60"
    ):
        recur.bysecond = invalid_second
    with pytest.raises(
        InvalidCalendar, match="BYSECOND values must be between 0 and 60"
    ):
        recur.bysecond = [0, invalid_second]


@pytest.mark.parametrize("stored", [-1, 61, "abc", True])
def test_directly_assigned_invalid_bysecond_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=MINUTELY")
    recur["BYSECOND"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.bysecond


def test_bysecond_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=MINUTELY;BYSECOND=0,30,60")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.bysecond == (0, 30, 60)
