"""Tests for the vRecur.bysetpos accessor (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.integer import vInt


def test_bysetpos_returns_empty_tuple_when_absent():
    """BYSETPOS is not set at all."""
    assert vRecur.from_ical("FREQ=YEARLY").bysetpos == ()


def test_bysetpos_returns_empty_tuple_when_empty_list():
    """If an empty list is in there, an empty tuple is returned."""
    recur = vRecur(FREQ=["MONTHLY"], BYSETPOS=[])
    assert recur.bysetpos == ()


def test_bysetpos_returns_single_value():
    assert vRecur.from_ical(
        "FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1"
    ).bysetpos == (-1,)


def test_bysetpos_returns_multiple_values():
    assert vRecur.from_ical("FREQ=YEARLY;BYDAY=SU;BYSETPOS=1,2,-1").bysetpos == (
        1,
        2,
        -1,
    )


def test_bysetpos_boundary_values_are_valid():
    assert vRecur.from_ical("FREQ=YEARLY;BYSETPOS=-366,-1,1,366").bysetpos == (
        -366,
        -1,
        1,
        366,
    )


def test_setting_bysetpos_with_single_int():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO")
    recur.bysetpos = -1
    assert recur.bysetpos == (-1,)
    assert recur["BYSETPOS"] == [vInt(-1)]
    assert recur.to_ical() == b"FREQ=MONTHLY;BYDAY=MO;BYSETPOS=-1"


def test_setting_bysetpos_with_list_of_ints():
    recur = vRecur.from_ical("FREQ=YEARLY;BYDAY=SU")
    recur.bysetpos = [1, 2, -1]
    assert recur.bysetpos == (1, 2, -1)
    assert recur["BYSETPOS"] == [vInt(1), vInt(2), vInt(-1)]
    assert recur.to_ical() == b"FREQ=YEARLY;BYDAY=SU;BYSETPOS=1,2,-1"


def test_setting_bysetpos_with_tuple_of_ints():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur.bysetpos = (1, -1)
    assert recur.bysetpos == (1, -1)
    assert recur["BYSETPOS"] == [vInt(1), vInt(-1)]


def test_setting_bysetpos_to_none_deletes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO;BYSETPOS=-1")
    recur.bysetpos = None
    assert recur.bysetpos == ()
    assert "BYSETPOS" not in recur
    assert recur.to_ical() == b"FREQ=MONTHLY;BYDAY=MO"


def test_setting_bysetpos_to_empty_sequence_deletes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO;BYSETPOS=-1")
    recur.bysetpos = []
    assert recur.bysetpos == ()
    assert "BYSETPOS" not in recur

    recur.bysetpos = [-1]
    recur.bysetpos = ()
    assert recur.bysetpos == ()
    assert "BYSETPOS" not in recur


def test_deleting_bysetpos_removes_value():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO;BYSETPOS=-1")
    del recur.bysetpos
    assert recur.bysetpos == ()
    assert "BYSETPOS" not in recur


def test_deleting_bysetpos_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    del recur.bysetpos
    assert recur.bysetpos == ()


def test_setting_bysetpos_to_non_int_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(TypeError):
        recur.bysetpos = "-1"
    with pytest.raises(TypeError):
        recur.bysetpos = [1, "-1"]


def test_setting_bysetpos_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(TypeError):
        recur.bysetpos = True
    with pytest.raises(TypeError):
        recur.bysetpos = [1, True]


def test_setting_bysetpos_to_zero_raises_invalid_calendar():
    """RFC 5545 Section 3.3.10 explicitly states the value 0 MUST NOT be used."""
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYSETPOS values must be between -366 and -1 or 1 and 366",
    ):
        recur.bysetpos = 0


@pytest.mark.parametrize("invalid_pos", [-367, 0, 367, 1000])
def test_setting_bysetpos_out_of_range_raises_invalid_calendar(invalid_pos):
    recur = vRecur.from_ical("FREQ=MONTHLY")
    with pytest.raises(
        InvalidCalendar,
        match="BYSETPOS values must be between -366 and -1 or 1 and 366",
    ):
        recur.bysetpos = invalid_pos
    with pytest.raises(
        InvalidCalendar,
        match="BYSETPOS values must be between -366 and -1 or 1 and 366",
    ):
        recur.bysetpos = [1, invalid_pos]


@pytest.mark.parametrize("stored", [-367, 0, 367, "abc", True])
def test_directly_assigned_invalid_bysetpos_raises_invalid_calendar(stored):
    recur = vRecur.from_ical("FREQ=MONTHLY")
    recur["BYSETPOS"] = [stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.bysetpos


def test_bysetpos_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.bysetpos == (-1,)
