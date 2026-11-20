r"""Line breaks in property values must not reach the serialized content lines.

Some value types, such as ``UNKNOWN``, are written verbatim.
A lone ``\r`` in such a value was written into the content line,
and parsers that end a line at a lone ``\r`` read the rest of the value
as a new property.

See https://github.com/PyCalendar/icalendar/issues/1555
and https://github.com/PyCalendar/icalendar/issues/1471.
"""

import pytest

from icalendar import Calendar, Event, vUnknown
from icalendar.parser import Contentline, Parameters
from icalendar.prop.factory import TypesFactory

INJECTED = "ATTENDEE:mailto:mallory@example.com"
LINE_BREAKS = {"CR": "\r", "LF": "\n", "CRLF": "\r\n"}
# The value types of jCal and xCal, and one that is not registered.
VALUE_TYPES = sorted(TypesFactory._jcal_value_types | {"x-custom"})


def assert_no_line_break_in_content_lines(ical: bytes) -> None:
    """Only the CRLF at the end of each content line may break a line."""
    assert b"\r" not in ical.replace(b"\r\n", b"")
    assert b"\n" not in ical.replace(b"\r\n", b"")


@pytest.mark.parametrize("value_type", VALUE_TYPES)
@pytest.mark.parametrize("line_break", LINE_BREAKS.values(), ids=LINE_BREAKS)
def test_jcal_value_cannot_add_a_content_line(value_type, line_break):
    """A line break from jCal is escaped or rejected, whatever the value type."""
    jcal = [
        "vcalendar",
        [],
        [
            [
                "vevent",
                [
                    ["uid", {}, "text", "1"],
                    ["x-prop", {}, value_type, f"a{line_break}{INJECTED}"],
                ],
                [],
            ]
        ],
    ]
    try:
        ical = Calendar.from_jcal(jcal).to_ical()
    except ValueError:
        return
    assert_no_line_break_in_content_lines(ical)


@pytest.mark.parametrize("value_type", VALUE_TYPES)
@pytest.mark.parametrize(
    "line_break", ["&#13;", "&#10;", "&#13;&#10;"], ids=["CR", "LF", "CRLF"]
)
def test_xcal_value_cannot_add_a_content_line(value_type, line_break):
    """A line break from xCal is escaped or rejected, whatever the value type."""
    xcal = (
        '<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0"><vcalendar>'
        f"<properties><x-prop><{value_type}>a{line_break}{INJECTED}</{value_type}>"
        "</x-prop></properties></vcalendar></icalendar>"
    ).encode()
    try:
        ical = Calendar.from_xcal(xcal)[0].to_ical()
    except ValueError:
        return
    assert_no_line_break_in_content_lines(ical)


@pytest.mark.parametrize("line_break", LINE_BREAKS.values(), ids=LINE_BREAKS)
def test_unknown_value_with_line_break_is_not_serialized(line_break):
    """UNKNOWN values are verbatim, so a line break cannot be escaped."""
    event = Event()
    event.add("X-PROP", vUnknown(f"a{line_break}{INJECTED}"))
    with pytest.raises(ValueError, match="unescaped new line"):
        event.to_ical()


@pytest.mark.parametrize(("name", "value"), [("X-PROP", "a\rb"), ("X-A\rB", "ab")])
def test_contentline_from_parts_rejects_a_carriage_return(name, value):
    with pytest.raises(ValueError, match="unescaped new line"):
        Contentline.from_parts(name, Parameters(), vUnknown(value))


def test_contentline_keeps_a_carriage_return_when_parsing():
    r"""Parsing stays lenient, only the serialization rejects a lone ``\r``."""
    assert Contentline("X-PROP:a\rb").parts()[2] == "a\rb"
