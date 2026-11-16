import datetime
import sys

import pytest

from icalendar import Calendar
from icalendar.parser import content_line


@pytest.mark.parametrize(
    ("field", "expected_value"),
    [
        ("PRODID", "-//Plönë.org//NONSGML plone.app.event//EN"),
        ("X-WR-CALDESC", "test non ascii: äöü ÄÖÜ €"),
    ],
)
def test_calendar_from_ical_respects_unicode(field, expected_value, calendars):
    cal = calendars.calendar_with_unicode
    assert cal[field].to_ical().decode("utf-8") == expected_value


@pytest.mark.parametrize(
    ("test_input", "field", "expected_value"),
    [
        ("event_with_unicode_fields", "SUMMARY", "Non-ASCII Test: ÄÖÜ äöü €"),
        (
            "event_with_unicode_fields",
            "DESCRIPTION",
            "icalendar should be able to handle non-ascii: €äüöÄÜÖ.",
        ),
        ("event_with_unicode_fields", "LOCATION", "Tribstrül"),
        # Non-unicode characters in summary
        # https://github.com/collective/icalendar/issues/64
        ("issue_64_event_with_non_ascii_summary", "SUMMARY", "åäö"),
        # Unicode characters in summary
        ("issue_64_event_with_ascii_summary", "SUMMARY", "abcdef"),
    ],
)
def test_event_from_ical_respects_unicode(test_input, field, expected_value, events):
    event = events[test_input]
    assert event[field].to_ical().decode("utf-8") == expected_value


@pytest.mark.parametrize(
    ("test_input", "expected_output"),
    [
        # chokes on umlauts in ORGANIZER
        # https://github.com/collective/icalendar/issues/101
        ("issue_101_icalendar_chokes_on_umlauts_in_organizer", "acme, ädmin"),
        ("event_with_unicode_organizer", "Джон Доу"),
    ],
)
def test_events_parameter_unicoded(events, test_input, expected_output):
    assert events[test_input]["ORGANIZER"].params["CN"] == expected_output


def test_parses_event_with_non_ascii_tzid_issue_237(calendars, in_timezone):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    start = calendars.issue_237_fail_to_parse_timezone_with_non_ascii_tzid.walk(
        "VEVENT"
    )[0].decoded("DTSTART")
    expected = in_timezone(datetime.datetime(2017, 5, 11, 13, 30), "America/Sao_Paulo")
    assert not calendars.issue_237_fail_to_parse_timezone_with_non_ascii_tzid.errors
    assert start == expected


def test_parses_timezone_with_non_ascii_tzid_issue_237(timezones):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    assert timezones.issue_237_brazilia_standard["tzid"] == "(UTC-03:00) Brasília"


@pytest.mark.parametrize("timezone_name", ["standard", "daylight"])
def test_parses_timezone_with_non_ascii_tzname_issue_273(timezones, timezone_name):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    assert (
        timezones.issue_237_brazilia_standard.walk(timezone_name)[0]["TZNAME"]
        == f"Brasília {timezone_name}"
    )


def test_broken_property(calendars):
    """
    Test if error messages are encoded properly.
    """
    for event in calendars.broken_ical.walk("vevent"):
        assert len(event.errors) == 1, "Not the right amount of errors."
        error = event.errors[0][1]
        assert error.startswith("Content line could not be parsed into parts")


def test_apple_xlocation(calendars):
    """
    Test if we support base64 encoded binary data in parameter values.
    """
    for event in calendars.x_location.walk("vevent"):
        assert len(event.errors) == 0, "Got too many errors"


def test_charset_parameter_decodes_legacy_non_utf8_value_issue_2078(
    charset_param_regex,
):
    """A legacy CHARSET parameter declares the encoding of the property
    value: latin-1 bytes decode with the declared charset instead of
    coming back as U+FFFD replacement characters (issue #2078).
    """
    ics = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//EN\r\n"
        b"BEGIN:VEVENT\r\nUID:1\r\nDTSTART:20261108T190000Z\r\n"
        b"SUMMARY;CHARSET=ISO-8859-1:Caf\xe9 Meeting\r\n"
        b"END:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    assert str(event["SUMMARY"]) == "Caf\u00e9 Meeting"


def test_unknown_charset_falls_back_gracefully_issue_2078(charset_param_regex):
    """An unknown CHARSET must not raise; the value degrades exactly as
    it did before the CHARSET parameter was honored (issue #2078)."""
    ics = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//EN\r\n"
        b"BEGIN:VEVENT\r\nUID:1\r\n"
        b"SUMMARY;CHARSET=BOGUS-XYZ:Caf\xe9 Meeting\r\n"
        b"END:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    assert "Meeting" in str(event["SUMMARY"])


@pytest.fixture(params=["py311", "py310"])
def charset_param_regex(request, monkeypatch):
    """Run with the CHARSET regex of Python 3.11+ and of Python 3.10.

    Python 3.10 has no possessive quantifiers, so it uses a simpler regex.
    Both are tested where they can be compiled.
    """
    if request.param == "py310":
        monkeypatch.setattr(
            content_line,
            "CHARSET_PARAM_BYTES",
            content_line._CHARSET_PARAM_BYTES_PY310,
        )
    elif sys.version_info < (3, 11):
        pytest.skip("Possessive quantifiers need Python 3.11 or later.")


def test_charset_text_inside_quoted_param_value_is_not_a_directive_issue_2078(
    charset_param_regex,
):
    """UTF-8 text with a quoted parameter value mentioning CHARSET= must
    still decode as UTF-8, not as the encoding named in the quotes.

    RFC 5545 §3.1.4 states that there is no property parameter to declare
    the charset of a value (iCalendar text is UTF-8), so CHARSET is not a
    conforming parameter at all — an unquoted top-level ``CHARSET=`` is only
    tolerated as a legacy marker of pre-RFC 5545 producers (issue #2078).
    Inside a quoted parameter value it is plain data: RFC 5545 §3.1 defines
    ``quoted-string = DQUOTE *QSAFE-CHAR DQUOTE`` with QSAFE-CHAR being any
    character except CONTROL and DQUOTE, so ";" and "=" (and thus the text
    ``;CHARSET=ISO-8859-1``) may occur inside the quotes without forming a
    second parameter.

    The ``DESCRIPTION`` line makes the whole file invalid UTF-8, so the
    per-line CHARSET scan runs: the ``SUMMARY`` line is valid UTF-8 but
    must still not be decoded with the charset named inside its quoted
    parameter value, while the real directive on ``DESCRIPTION`` is
    honored.
    """
    summary = "Caf\u00e9 Meeting"
    description = "Caf\u00e9 R\u00e9sum\u00e9"  # latin-1 bytes below
    ics = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//EN\r\n"
        b"BEGIN:VEVENT\r\nUID:1\r\n"
        b'SUMMARY;ALTREP="cid:x;CHARSET=ISO-8859-1":'
        + summary.encode("utf-8")
        + b"\r\nDESCRIPTION;CHARSET=ISO-8859-1:"
        + description.encode("iso-8859-1")
        + b"\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    assert str(event["SUMMARY"]) == summary
    assert str(event["DESCRIPTION"]) == description


def test_vestigial_charset_in_valid_utf8_does_not_override_issue_2078(
    charset_param_regex,
):
    """A file that is valid UTF-8 parses as UTF-8 even if it still
    carries a vestigial legacy ``CHARSET`` parameter.

    Re-encoded migrations of legacy files can keep the old ``CHARSET``
    parameter while the bytes are already UTF-8. RFC 5545 §3.1.4 makes
    UTF-8 the charset of a conforming stream, so valid UTF-8 input must
    parse exactly as it did before this parameter was honored: the
    declared charset must not turn the UTF-8 text into mojibake
    (issue #2078).
    """
    summary = "Caf\u00e9 Meeting"
    ics = (
        b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//EN\r\n"
        b"BEGIN:VEVENT\r\nUID:1\r\n"
        b"SUMMARY;CHARSET=ISO-8859-1:"
        + summary.encode("utf-8")
        + b"\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    assert str(event["SUMMARY"]) == summary
