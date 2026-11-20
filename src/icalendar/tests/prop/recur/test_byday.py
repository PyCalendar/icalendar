"""Tests for the vRecur.byday and vRecur.byweekday accessors (issue #1851)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur, vWeekday


def test_byday_returns_empty_tuple_when_absent():
    assert vRecur.from_ical("FREQ=DAILY").byday == ()


def test_byday_returns_empty_tuple_when_empty_list():
    recur = vRecur(FREQ=["DAILY"], BYDAY=[])
    assert recur.byday == ()


def test_byday_returns_single_weekday():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO")
    assert recur.byday == (vWeekday("MO"),)
    assert isinstance(recur.byday[0], vWeekday)


def test_byday_returns_multiple_weekdays():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR")
    assert recur.byday == (
        vWeekday("MO"),
        vWeekday("TU"),
        vWeekday("WE"),
        vWeekday("TH"),
        vWeekday("FR"),
    )


def test_byday_returns_weekdays_with_positions():
    recur = vRecur.from_ical("FREQ=MONTHLY;BYDAY=+1MO,-2FR")
    assert recur.byday == (vWeekday("+1MO"), vWeekday("-2FR"))


def test_byweekday_alias_getter():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=SA,SU")
    assert recur.byweekday == (vWeekday("SA"), vWeekday("SU"))


def test_setting_byday_with_single_str():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.byday = "MO"
    assert recur.byday == (vWeekday("MO"),)
    assert recur.to_ical() == b"FREQ=WEEKLY;BYDAY=MO"


def test_setting_byday_with_vweekday():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.byday = vWeekday("+2TU")
    assert recur.byday == (vWeekday("+2TU"),)


def test_setting_byday_with_iterable_of_strings():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.byday = ["MO", "WE", "FR"]
    assert recur.byday == (vWeekday("MO"), vWeekday("WE"), vWeekday("FR"))
    assert recur.to_ical() == b"FREQ=WEEKLY;BYDAY=MO,WE,FR"


def test_setting_byday_with_iterable_of_vweekdays():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.byday = (vWeekday("SA"), vWeekday("SU"))
    assert recur.byday == (vWeekday("SA"), vWeekday("SU"))


def test_setting_byday_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO,TU")
    recur.byday = None
    assert recur.byday == ()
    assert "BYDAY" not in recur


def test_setting_byday_to_empty_sequence_deletes_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO")
    recur.byday = []
    assert recur.byday == ()
    assert "BYDAY" not in recur


def test_deleting_byday_removes_the_value():
    recur = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO")
    del recur.byday
    assert recur.byday == ()
    assert "BYDAY" not in recur


def test_byweekday_alias_setter_and_deleter():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    recur.byweekday = ["TU", "TH"]
    assert recur.byday == (vWeekday("TU"), vWeekday("TH"))
    del recur.byweekday
    assert recur.byday == ()
    assert "BYDAY" not in recur


def test_setting_byday_with_invalid_weekday_string_raises():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(InvalidCalendar):
        recur.byday = "INVALID"


def test_setting_byday_with_invalid_type_raises():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(TypeError):
        recur.byday = 42


def test_setting_byday_with_invalid_element_type_raises():
    recur = vRecur.from_ical("FREQ=WEEKLY")
    with pytest.raises(TypeError):
        recur.byday = ["MO", 123]


def test_byday_getter_raises_invalid_calendar_on_corrupt_data():
    recur = vRecur(FREQ=["WEEKLY"], BYDAY=["NOT_A_DAY"])
    with pytest.raises(InvalidCalendar):
        _ = recur.byday
