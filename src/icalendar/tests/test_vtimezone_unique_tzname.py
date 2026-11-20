"""Subcomponents of a VTIMEZONE without TZNAME get unique names.

Timezone.get_transitions names each STANDARD and DAYLIGHT subcomponent
without a TZNAME after its TZID, DTSTART and offsets.
Equal subcomponents used to get one more ``_1`` appended for each earlier one,
so n of them took cubic time and built names of length 2n.
This made parsing an untrusted calendar with the pytz provider slow.
"""

from icalendar import Calendar, Timezone

SUBCOMPONENT = (
    "BEGIN:STANDARD\r\n"
    "DTSTART:19701101T020000\r\n"
    "TZOFFSETFROM:-0400\r\n"
    "TZOFFSETTO:-0500\r\n"
    "END:STANDARD\r\n"
)


def vtimezone(count: int) -> Timezone:
    """Return a VTIMEZONE with count equal subcomponents without TZNAME."""
    calendar = Calendar.from_ical(
        "BEGIN:VCALENDAR\r\nBEGIN:VTIMEZONE\r\nTZID:X-Custom\r\n"
        + SUBCOMPONENT * count
        + "END:VTIMEZONE\r\nEND:VCALENDAR\r\n"
    )
    return calendar.timezones[0]


def test_equal_subcomponents_get_unique_names():
    """Each subcomponent gets its own name."""
    _, transition_info = vtimezone(3).get_transitions()
    names = sorted(name for _, _, name in transition_info)
    base = "X-Custom_19701101T020000_-0400_-0500"
    assert names == [base, f"{base}_1", f"{base}_2"]


def test_many_equal_subcomponents_keep_short_names():
    """The names do not grow with the number of subcomponents."""
    count = 2000
    _, transition_info = vtimezone(count).get_transitions()
    names = {name for _, _, name in transition_info}
    assert len(names) == count
    assert max(len(name) for name in names) < 60


def test_suffix_skips_names_in_use():
    """A suffix that is already in use is skipped."""
    names = {"EST": 1, "EST_1": 1}
    assert Timezone._make_unique_tzname("EST", names) == "EST_2"
    assert Timezone._make_unique_tzname("EST_1", names) == "EST_1_1"
    assert Timezone._make_unique_tzname("EST", names) == "EST_3"
