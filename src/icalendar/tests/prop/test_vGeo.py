import re

import pytest

from icalendar import Event
from icalendar.prop import vGeo

RFC5545_FLOAT = re.compile(r"^[+-]?\d+(?:\.\d+)?$")


@pytest.mark.parametrize(
    ("geo", "expected"),
    [
        ((0.00001, -0.00002), "0.00001;-0.00002"),
        ((1e16, -1e16), "10000000000000000;-10000000000000000"),
        ((37.386013, -122.082932), "37.386013;-122.082932"),
        ((1.2, 3.0), "1.2;3.0"),
    ],
)
def test_geo_has_no_exponent(geo, expected):
    """FLOAT has no exponent notation, see RFC 5545 3.3.7."""
    ical = vGeo(geo).to_ical()
    assert ical == expected
    assert all(RFC5545_FLOAT.match(part) for part in ical.split(";"))


def test_event_geo_line_has_no_exponent():
    """The reported case: a GEO near the equator used to be written as 1e-05."""
    event = Event()
    event.add("GEO", (0.00001, -0.00002))
    assert "GEO:0.00001;-0.00002" in event.to_ical().decode()


def test_written_geo_parses_back():
    geo = (1e-5, -2e-5)
    assert vGeo.from_ical(vGeo(geo).to_ical()) == geo
