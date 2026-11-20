"""Test vRecur.ical_value, see issue 876."""

from datetime import date, datetime

from icalendar import Event
from icalendar.prop import vRecur


def test_ical_value_native_values():
    """The rule parts are returned as native Python values."""
    recur = vRecur.from_ical("FREQ=WEEKLY;COUNT=3;BYDAY=1SU,MO;BYMONTH=11;WKST=MO")
    value = recur.ical_value
    assert value == {
        "FREQ": ["WEEKLY"],
        "COUNT": [3],
        "BYDAY": ["1SU", "MO"],
        "BYMONTH": [11],
        "WKST": ["MO"],
    }
    assert type(value) is dict
    assert type(value["FREQ"][0]) is str
    assert type(value["COUNT"][0]) is int
    assert type(value["BYMONTH"][0]) is int


def test_ical_value_until():
    """UNTIL is a date or a datetime."""
    assert vRecur.from_ical("FREQ=DAILY;UNTIL=20240102").ical_value["UNTIL"] == [
        date(2024, 1, 2)
    ]
    assert vRecur.from_ical("FREQ=DAILY;UNTIL=20240102T030405").ical_value["UNTIL"] == [
        datetime(2024, 1, 2, 3, 4, 5)
    ]


def test_ical_value_skip_and_rscale():
    """RFC 7529 parts are plain strings."""
    value = vRecur.from_ical("RSCALE=GREGORIAN;FREQ=YEARLY;SKIP=FORWARD").ical_value
    assert value == {"RSCALE": ["GREGORIAN"], "FREQ": ["YEARLY"], "SKIP": ["FORWARD"]}
    assert type(value["SKIP"][0]) is str


def test_ical_value_is_a_copy():
    """Changing the result does not change the recurrence."""
    recur = vRecur.from_ical("FREQ=DAILY;COUNT=2")
    recur.ical_value["COUNT"].append(5)
    assert recur.to_ical() == b"FREQ=DAILY;COUNT=2"


def test_decoded_uses_ical_value():
    """Component.decoded() returns the native values."""
    event = Event()
    event.add("RRULE", {"FREQ": "DAILY", "COUNT": 2})
    assert event.decoded("RRULE") == {"FREQ": ["DAILY"], "COUNT": [2]}
