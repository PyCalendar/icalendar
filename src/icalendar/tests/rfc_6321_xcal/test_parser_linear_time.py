"""Regression test for the quadratic run time of the xCal parser.

``XCalParser.done()`` copied the remaining child elements into a new list for
every element it parsed, and ``_parse_tag()`` deleted from the front of that
list, so an xCal document with many properties, parameters, values or
components took seconds to minutes to parse. The children are kept in a deque
now and parsing is linear in the number of elements.
"""

import time

import pytest

from icalendar import Calendar

XCAL = (
    '<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">'
    "<vcalendar>{}</vcalendar></icalendar>"
)


def properties(n):
    return XCAL.format(
        "<properties>" + "<x-a><text>a</text></x-a>" * n + "</properties>"
    )


def values(n):
    return XCAL.format(
        "<properties><categories>" + "<text>a</text>" * n + "</categories></properties>"
    )


def parameters(n):
    return XCAL.format(
        "<properties><summary><parameters><x-p>"
        + "<text>a</text>" * n
        + "</x-p></parameters><text>s</text></summary></properties>"
    )


def components(n):
    return XCAL.format("<components>" + "<x-c/>" * n + "</components>")


@pytest.mark.parametrize(
    ("xcal", "n", "count"),
    [
        (properties, 100_000, lambda calendar, n: len(calendar["X-A"]) == n),
        (values, 500_000, lambda calendar, n: len(calendar["CATEGORIES"].cats) == n),
        (
            parameters,
            300_000,
            lambda calendar, n: len(calendar["SUMMARY"].params["X-P"]) == n,
        ),
        (components, 100_000, lambda calendar, n: len(calendar.subcomponents) == n),
    ],
)
def test_many_elements_parse_quickly(xcal, n, count):
    """Parsing is linear in the number of elements.

    The unpatched parser needs 10 s to minutes for these documents; the bound
    is generous enough to never flake on slow CI while still catching a return
    of the quadratic behaviour.
    """
    start = time.perf_counter()
    calendar = Calendar.from_xcal(xcal(n).encode())[0]
    assert time.perf_counter() - start < 5
    assert count(calendar, n)
