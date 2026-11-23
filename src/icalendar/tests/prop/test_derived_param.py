r"""DERIVED property parameter from :rfc:`9073`.

:rfc:`9073#section-5.3` defines DERIVED to mark that a property's value was
computed from other property values and so MUST NOT be edited directly.
The RFC's own example is a STYLED-DESCRIPTION rendering generated from
another STYLED-DESCRIPTION -- a value type not implemented in this codebase
yet (see :issue:`656`). Exercised here on :class:`~icalendar.prop.text.vText`
instead, since DERIVED may be specified on any property.
"""

from icalendar import vText


def test_derived_default_is_false():
    """DERIVED defaults to False when absent, per RFC 9073 5.3."""
    comment = vText("Generated summary")
    assert comment.DERIVED is False


def test_derived_round_trips_as_bool():
    """Setting DERIVED to True serializes as DERIVED=TRUE and reads back True."""
    comment = vText("Generated summary")
    comment.DERIVED = True
    assert comment.DERIVED is True
    assert comment.params["DERIVED"] == "TRUE"
