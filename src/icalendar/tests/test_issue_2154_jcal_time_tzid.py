"""Preserve TIME timezones through the jCal component parsing entry point."""

from copy import deepcopy
from datetime import time

import pytest

from icalendar import Event
from icalendar.prop import vTime
from icalendar.timezone.tzid import tzid_from_dt


@pytest.mark.parametrize("zone", ["Asia/Dhaka", "Europe/Berlin", "UTC"])
def test_jcal_time_retains_timezone(tzp, zone):
    """Parsing and reserializing a TIME must preserve its timezone semantics."""
    expected = vTime(tzp.localize(time(8, 30), zone))
    property_jcal = expected.to_jcal("x-time")
    original = deepcopy(property_jcal)

    parsed = vTime.from_jcal(property_jcal)
    assert tzid_from_dt(parsed.dt) == tzid_from_dt(expected.dt)
    assert parsed.to_jcal("x-time") == property_jcal

    event_jcal = ["vevent", [property_jcal], []]
    event = Event.from_jcal(event_jcal)
    assert tzid_from_dt(event["X-TIME"].dt) == tzid_from_dt(expected.dt)
    assert event.to_jcal() == event_jcal
    assert property_jcal == original


def test_jcal_floating_time_stays_floating():
    """A time without a TZID or UTC suffix remains floating."""
    property_jcal = ["x-time", {}, "time", "08:30:00"]
    parsed = vTime.from_jcal(property_jcal)
    assert parsed.dt == time(8, 30)
    assert parsed.dt.tzinfo is None
    assert parsed.to_jcal("x-time") == property_jcal
