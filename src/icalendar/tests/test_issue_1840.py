"""Test that the enums accept case-insensitive values.

The values of the enums in :mod:`icalendar.enums` are not enclosed in
double quotes, so they are case-insensitive as of :rfc:`5545`, section 3.1:
"All names of properties, property parameters, enumerated property values
and property parameter values are case-insensitive."

See https://github.com/collective/icalendar/issues/1840
"""

import pytest

from icalendar import enums

CASE_INSENSITIVE_ENUMS = [
    enums.BUSYTYPE,
    enums.CLASS,
    enums.CUTYPE,
    enums.FBTYPE,
    enums.PARTSTAT,
    enums.RANGE,
    enums.RELATED,
    enums.RELTYPE,
    enums.ROLE,
    enums.STATUS,
    enums.TRANSP,
    enums.VALUE,
]


def test_partstat_from_the_issue():
    """The example of the issue works."""
    assert (
        enums.PARTSTAT("needs-action")
        == enums.PARTSTAT("NEEDS-ACTION")
        == enums.PARTSTAT.NEEDS_ACTION
    )


@pytest.mark.parametrize("enum", CASE_INSENSITIVE_ENUMS, ids=lambda enum: enum.__name__)
def test_every_value_can_be_looked_up_in_any_case(enum):
    """Every value can be looked up in lower, upper and mixed case."""
    for member in enum:
        assert enum(member.value.lower()) is member
        assert enum(member.value.upper()) is member
        assert enum(member.value.title()) is member


@pytest.mark.parametrize("enum", CASE_INSENSITIVE_ENUMS, ids=lambda enum: enum.__name__)
def test_values_keep_their_case(enum):
    """Looking a value up in another case returns the canonical value."""
    for member in enum:
        assert enum(member.value.lower()).value == member.value
        assert enum(member.value.title()).value == member.value


@pytest.mark.parametrize("enum", CASE_INSENSITIVE_ENUMS, ids=lambda enum: enum.__name__)
def test_unknown_values_still_fail(enum):
    """Values that are unknown, regardless of their case, are an error."""
    with pytest.raises(ValueError):
        enum("this-is-not-a-known-value")
    with pytest.raises(ValueError):
        enum("THIS-IS-NOT-A-KNOWN-VALUE")
