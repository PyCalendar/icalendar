"""Tests for the vRecur.bymonth accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vMonth, vRecur


def test_bymonth_returns_empty_tuple_when_absent():
    """BYMONTH is not set at all."""
    assert vRecur.from_ical("FREQ=YEARLY").bymonth == ()


def test_bymonth_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["YEARLY"], BYMONTH=[])
    assert recur.bymonth == ()


def test_bymonth_returns_single_value():
    bymonth = vRecur.from_ical("FREQ=YEARLY;BYMONTH=6").bymonth
    assert bymonth == (vMonth(6),)
    assert bymonth[0] == 6
    assert isinstance(bymonth[0], vMonth)


def test_bymonth_returns_multiple_values():
    bymonth = vRecur.from_ical("FREQ=YEARLY;BYMONTH=1,6,12").bymonth
    assert bymonth == (vMonth(1), vMonth(6), vMonth(12))
    assert all(isinstance(m, vMonth) for m in bymonth)


def test_bymonth_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYMONTH=1").bymonth == (vMonth(1),)
    assert vRecur.from_ical("FREQ=YEARLY;BYMONTH=12").bymonth == (vMonth(12),)


def test_bymonth_leap_month_is_valid():
    """RFC 7529 allows leap months like 5L."""
    bymonth = vRecur.from_ical("FREQ=YEARLY;BYMONTH=5L").bymonth
    assert len(bymonth) == 1
    assert bymonth[0] == 5
    assert bymonth[0].leap is True


def test_setting_bymonth_with_single_int():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.bymonth = 6
    assert recur.bymonth == (vMonth(6),)
    assert isinstance(recur["BYMONTH"][0], vMonth)
    assert recur.to_ical() == b"FREQ=YEARLY;BYMONTH=6"


def test_setting_bymonth_with_vmonth():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.bymonth = vMonth("5L")
    assert recur.bymonth == (vMonth("5L"),)
    assert recur.bymonth[0].leap is True
    assert recur.to_ical() == b"FREQ=YEARLY;BYMONTH=5L"


def test_setting_bymonth_with_list():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.bymonth = [1, 12]
    assert recur.bymonth == (vMonth(1), vMonth(12))
    assert recur.to_ical() == b"FREQ=YEARLY;BYMONTH=1,12"


def test_setting_bymonth_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYMONTH=6")
    recur.bymonth = None
    assert recur.bymonth == ()
    assert "BYMONTH" not in recur


def test_setting_bymonth_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYMONTH=6")
    recur.bymonth = []
    assert recur.bymonth == ()
    assert "BYMONTH" not in recur

    recur.bymonth = [6]
    recur.bymonth = ()
    assert recur.bymonth == ()
    assert "BYMONTH" not in recur


def test_deleting_bymonth_removes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYMONTH=6")
    del recur.bymonth
    assert recur.bymonth == ()
    assert "BYMONTH" not in recur


def test_deleting_bymonth_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.bymonth
    assert recur.bymonth == ()


def test_setting_bymonth_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.bymonth = [1, object()]


def test_setting_bymonth_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.bymonth = True
    with pytest.raises(TypeError):
        recur.bymonth = [1, True]


@pytest.mark.parametrize("invalid_month", [-1, 0, 13, 100])
def test_setting_bymonth_out_of_range_raises_invalid_calendar(invalid_month):
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar, match="BYMONTH values must be between 1 and 12"
    ):
        recur.bymonth = invalid_month
    with pytest.raises(
        InvalidCalendar, match="BYMONTH values must be between 1 and 12"
    ):
        recur.bymonth = [1, invalid_month]


@pytest.mark.parametrize("stored", [-1, 0, 13, "abc", True])
def test_directly_assigned_invalid_bymonth_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["BYMONTH"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.bymonth


def test_bymonth_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=YEARLY;BYMONTH=1,6,12")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.bymonth == (vMonth(1), vMonth(6), vMonth(12))
