"""Tests for the vRecur.skip accessor (issue #1851, RFC 7529)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur, vSkip


def test_skip_returns_none_when_absent():
    assert vRecur.from_ical("FREQ=YEARLY").skip is None


def test_skip_returns_the_value():
    skip = vRecur.from_ical("FREQ=YEARLY;RSCALE=CHINESE;SKIP=FORWARD").skip
    assert skip == "FORWARD"
    assert isinstance(skip, vSkip)


def test_skip_returns_first_value_when_multiple_are_present():
    recur = vRecur(FREQ=["YEARLY"], SKIP=[vSkip("FORWARD"), vSkip("BACKWARD")])
    assert recur.skip == "FORWARD"


def test_skip_returns_none_when_value_is_an_empty_list():
    recur = vRecur(FREQ=["YEARLY"], SKIP=[])
    assert recur.skip is None


def test_setting_skip_stores_a_vskip():
    recur = vRecur.from_ical("FREQ=YEARLY;RSCALE=ISLAMIC")
    recur.skip = "BACKWARD"
    assert recur.skip == "BACKWARD"
    assert isinstance(recur["SKIP"][0], vSkip)
    assert recur.to_ical() == b"RSCALE=ISLAMIC;FREQ=YEARLY;SKIP=BACKWARD"


def test_setting_skip_to_vskip_stores_the_value():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.skip = vSkip.OMIT
    assert recur.skip == "OMIT"


def test_setting_skip_to_none_deletes_the_value():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    recur.skip = None
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_removes_the_value():
    recur = vRecur.from_ical("FREQ=YEARLY;SKIP=FORWARD")
    del recur.skip
    assert recur.skip is None
    assert "SKIP" not in recur


def test_deleting_skip_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.skip
    assert recur.skip is None


def test_directly_assigned_string_is_returned_as_vskip():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = "OMIT"
    assert recur.skip == "OMIT"
    assert isinstance(recur.skip, vSkip)


def test_skip_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=YEARLY;RSCALE=CHINESE;SKIP=FORWARD")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.skip == recur.skip
    assert isinstance(roundtripped.skip, vSkip)


def test_setting_skip_matches_parsed_vrecur():
    """Assigning SKIP must produce the same vRecur as parsing it.

    ``from_ical`` stores ``SKIP`` as a one-item list of ``vSkip``, so
    the setter keeps that representation rather than a bare value.
    """
    parsed = vRecur.from_ical("FREQ=YEARLY;RSCALE=CHINESE;SKIP=FORWARD")
    assigned = vRecur.from_ical("FREQ=YEARLY;RSCALE=CHINESE")
    assigned.skip = "FORWARD"
    assert assigned == parsed
    assert assigned["SKIP"] == parsed["SKIP"]
    assert isinstance(assigned["SKIP"], list)
    assert assigned.to_ical() == parsed.to_ical()


def test_setting_skip_to_non_string_type_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.skip = 1


def test_setting_skip_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.skip = True


def test_setting_skip_to_invalid_skip_value_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(
        InvalidCalendar, match="SKIP must be OMIT, BACKWARD, or FORWARD"
    ):
        recur.skip = "INVALID"


@pytest.mark.parametrize("stored", ["INVALID", "", ["INVALID"]])
def test_directly_assigned_unreadable_skip_raises_invalid_calendar(stored):
    """The only route to an unreadable SKIP is assigning it directly, past
    the parser. Reading it reports InvalidCalendar rather than letting a
    bare ValueError escape."""
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["SKIP"] = stored
    with pytest.raises(
        InvalidCalendar, match="SKIP must be OMIT, BACKWARD, or FORWARD"
    ):
        recur.skip
