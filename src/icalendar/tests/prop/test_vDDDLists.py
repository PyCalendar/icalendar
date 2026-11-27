"""Test vDDDLists property."""

from datetime import date, datetime, timedelta, timezone

from icalendar import Event
from icalendar.prop import vDDDLists


def test_ical_value_datetimes():
    """ical_value returns the datetimes as a plain list."""
    values = [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 2, 10, 0)]
    ical_value = vDDDLists(values).ical_value
    assert ical_value == values
    assert type(ical_value) is list


def test_ical_value_dates():
    """ical_value returns dates as dates."""
    values = [date(2025, 1, 1), date(2025, 1, 2)]
    assert vDDDLists(values).ical_value == values


def test_ical_value_period():
    """ical_value returns a period as its (start, end or duration) tuple."""
    period = (datetime(2025, 1, 1, 10, 0), timedelta(hours=1))
    assert vDDDLists([period]).ical_value == [period]


def test_decoded_exdate_returns_native_values():
    """Component.decoded returns the dates, not the vDDDLists object."""
    event = Event.from_ical(
        "BEGIN:VEVENT\r\nEXDATE:20250101T100000Z,20250102T100000Z\r\nEND:VEVENT\r\n"
    )
    assert event.decoded("EXDATE") == [
        datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        datetime(2025, 1, 2, 10, 0, tzinfo=timezone.utc),
    ]


def test_decoded_multiple_exdate_lines():
    """Each EXDATE line decodes to its own list."""
    event = Event.from_ical(
        "BEGIN:VEVENT\r\n"
        "EXDATE;VALUE=DATE:20250101\r\n"
        "EXDATE;VALUE=DATE:20250102,20250103\r\n"
        "END:VEVENT\r\n"
    )
    assert event.decoded("EXDATE") == [
        [date(2025, 1, 1)],
        [date(2025, 1, 2), date(2025, 1, 3)],
    ]
