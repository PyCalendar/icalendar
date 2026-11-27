"""Tests for the vRecur.byweekno accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vInt


def test_byweekno_returns_empty_tuple_when_absent():
    """BYWEEKNO is not set at all."""
    assert vRecur.from_ical("FREQ=YEARLY").byweekno == ()


def test_byweekno_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["YEARLY"], BYWEEKNO=[])
    assert recur.byweekno == ()


def test_byweekno_returns_single_value():
    assert vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=20").byweekno == (20,)


def test_byweekno_returns_multiple_values():
    assert vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=1,20,53").byweekno == (
        1,
        20,
        53,
    )


def test_byweekno_negative_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=-1,-53").byweekno == (-1, -53)


def test_byweekno_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=-53,-1,1,53").byweekno == (
        -53,
        -1,
        1,
        53,
    )


def test_setting_byweekno_with_single_int():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byweekno = 20
    assert recur.byweekno == (20,)
    assert isinstance(recur["BYWEEKNO"][0], vInt)
    assert recur.to_ical() == b"FREQ=YEARLY;BYWEEKNO=20"


def test_setting_byweekno_with_negative_int():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byweekno = -1
    assert recur.byweekno == (-1,)
    assert recur.to_ical() == b"FREQ=YEARLY;BYWEEKNO=-1"


def test_setting_byweekno_with_list():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.byweekno = [1, -1, 53]
    assert recur.byweekno == (1, -1, 53)
    assert recur.to_ical() == b"FREQ=YEARLY;BYWEEKNO=1,-1,53"


def test_setting_byweekno_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=20")
    recur.byweekno = None
    assert recur.byweekno == ()
    assert "BYWEEKNO" not in recur


def test_setting_byweekno_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=20")
    recur.byweekno = []
    assert recur.byweekno == ()
    assert "BYWEEKNO" not in recur

    recur.byweekno = [20]
    recur.byweekno = ()
    assert recur.byweekno == ()
    assert "BYWEEKNO" not in recur


def test_deleting_byweekno_removes_value():
    recur = vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=20")
    del recur.byweekno
    assert recur.byweekno == ()
    assert "BYWEEKNO" not in recur


def test_deleting_byweekno_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.byweekno
    assert recur.byweekno == ()


def test_setting_byweekno_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.byweekno = "20"
    with pytest.raises(TypeError):
        recur.byweekno = [1, "20"]


def test_setting_byweekno_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.byweekno = True
    with pytest.raises(TypeError):
        recur.byweekno = [1, True]


def test_setting_byweekno_to_zero_raises_invalid_calendar():
    """RFC 5545 Section 3.3.10 explicitly states the value 0 MUST NOT be used."""
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYWEEKNO values must be between -53 and -1 or 1 and 53",
    ):
        recur.byweekno = 0


@pytest.mark.parametrize("invalid_week", [-54, 0, 54, 100])
def test_setting_byweekno_out_of_range_raises_invalid_calendar(invalid_week):
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYWEEKNO values must be between -53 and -1 or 1 and 53",
    ):
        recur.byweekno = invalid_week
    with pytest.raises(
        InvalidCalendar,
        match="BYWEEKNO values must be between -53 and -1 or 1 and 53",
    ):
        recur.byweekno = [1, invalid_week]


@pytest.mark.parametrize("stored", [-54, 0, 54, "abc", True])
def test_directly_assigned_invalid_byweekno_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["BYWEEKNO"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.byweekno


def test_byweekno_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=YEARLY;BYWEEKNO=1,-1,53")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.byweekno == (1, -1, 53)
