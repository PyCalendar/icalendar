r"""SCHEMA property parameter from :rfc:`9073`.

:rfc:`9073#section-5.2` defines SCHEMA as a URI identifying the schema a
``STRUCTURED-DATA`` property value conforms to. ``STRUCTURED-DATA``
(:rfc:`9073#section-6.6`) is not implemented in this codebase yet (see
:issue:`656`), so SCHEMA is only defined in :mod:`icalendar.param` for now
and not attached to any property class. It is exercised here directly
against ``Parameters``.
"""

from icalendar.parser import Parameters


def test_schema_is_a_plain_parameter_not_yet_attached_to_a_property():
    """SCHEMA exists in icalendar.param but has no property class yet.

    STRUCTURED-DATA, the property SCHEMA belongs on, is not implemented
    (see :issue:`656`), so SCHEMA is only reachable through raw
    ``Parameters`` for now.
    """
    params = Parameters(SCHEMA="https://schema.org/FlightReservation")
    assert params["SCHEMA"] == "https://schema.org/FlightReservation"
