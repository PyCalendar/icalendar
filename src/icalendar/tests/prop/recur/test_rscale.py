"""Tests for the vRecur.rscale accessor (issue #1851, RFC 7529)."""

import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vRecur
from icalendar.prop.text import vText


def test_rscale_returns_none_when_absent():
    """RSCALE is not set at all."""
    assert vRecur.from_ical("FREQ=YEARLY").rscale is None


def test_rscale_returns_none_when_empty_list():
    """If an empty list is in there, None is returned."""
    recur = vRecur(FREQ=["YEARLY"], RSCALE=[])
    assert recur.rscale is None


def test_rscale_returns_scale_string():
    assert vRecur.from_ical("RSCALE=CHINESE;FREQ=YEARLY").rscale == "CHINESE"
    assert vRecur.from_ical("RSCALE=ETHIOPIC;FREQ=YEARLY").rscale == "ETHIOPIC"
    assert vRecur.from_ical("RSCALE=HEBREW;FREQ=YEARLY").rscale == "HEBREW"
    assert vRecur.from_ical("RSCALE=GREGORIAN;FREQ=YEARLY").rscale == "GREGORIAN"


def test_rscale_returns_uppercase():
    recur = vRecur(FREQ=["YEARLY"], RSCALE=["hebrew"])
    assert recur.rscale == "HEBREW"


def test_rscale_multiple_values_returns_first():
    recur = vRecur(FREQ=["YEARLY"], RSCALE=["CHINESE", "HEBREW"])
    assert recur.rscale == "CHINESE"


def test_setting_rscale_with_string():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.rscale = "CHINESE"
    assert recur.rscale == "CHINESE"
    assert recur["RSCALE"] == [vText("CHINESE")]
    assert recur.to_ical() == b"RSCALE=CHINESE;FREQ=YEARLY"


def test_setting_rscale_normalizes_to_uppercase():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.rscale = "islamic"
    assert recur.rscale == "ISLAMIC"
    assert recur.to_ical() == b"RSCALE=ISLAMIC;FREQ=YEARLY"


def test_setting_rscale_strips_whitespace():
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur.rscale = "  ethiopic  "
    assert recur.rscale == "ETHIOPIC"


def test_setting_rscale_to_none_deletes_value():
    recur = vRecur.from_ical("RSCALE=CHINESE;FREQ=YEARLY")
    recur.rscale = None
    assert recur.rscale is None
    assert "RSCALE" not in recur
    assert recur.to_ical() == b"FREQ=YEARLY"


def test_deleting_rscale_removes_value():
    recur = vRecur.from_ical("RSCALE=CHINESE;FREQ=YEARLY")
    del recur.rscale
    assert recur.rscale is None
    assert "RSCALE" not in recur


def test_deleting_rscale_when_absent_does_not_raise():
    recur = vRecur.from_ical("FREQ=YEARLY")
    del recur.rscale
    assert recur.rscale is None


def test_setting_rscale_to_non_string_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.rscale = 123
    with pytest.raises(TypeError):
        recur.rscale = ["CHINESE"]


def test_setting_rscale_to_bool_raises_type_error():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(TypeError):
        recur.rscale = True


def test_setting_rscale_to_empty_string_raises_invalid_calendar():
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(InvalidCalendar, match="RSCALE cannot be empty"):
        recur.rscale = ""
    with pytest.raises(InvalidCalendar, match="RSCALE cannot be empty"):
        recur.rscale = "   "


def test_setting_rscale_with_part_separator_raises_invalid_calendar():
    """RECUR has no escaping; RSCALE values cannot contain ';' or ','."""
    recur = vRecur.from_ical("FREQ=YEARLY")
    with pytest.raises(InvalidCalendar, match="RSCALE cannot contain"):
        recur.rscale = "CHINESE;FREQ=DAILY"
    with pytest.raises(InvalidCalendar, match="RSCALE cannot contain"):
        recur.rscale = "CHINESE,HEBREW"


@pytest.mark.parametrize(
    "invalid_stored", ["CHINESE;FREQ=YEARLY", "CHINESE,HEBREW", "", "   ", True]
)
def test_directly_assigned_invalid_rscale_raises_invalid_calendar(invalid_stored):
    recur = vRecur.from_ical("FREQ=YEARLY")
    recur["RSCALE"] = [invalid_stored]
    with pytest.raises(InvalidCalendar):
        _ = recur.rscale


def test_rscale_roundtrips_through_ical():
    recur = vRecur.from_ical("RSCALE=CHINESE;FREQ=YEARLY")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())
    assert roundtripped.rscale == "CHINESE"
