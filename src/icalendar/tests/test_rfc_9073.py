"""Test RFC 9073 Event Publishing Extensions to iCalendar.

See https://www.rfc-editor.org/rfc/rfc9073
and also https://github.com/PyCalendar/icalendar/issues/656
"""

import pytest

from icalendar import (
    PARTICIPANT_TYPE,
    PROXIMITY,
    RELTYPE,
    RESOURCE_TYPE,
    Location,
    Participant,
    Resource,
    vCalAddress,
    vText,
    vUri,
)


@pytest.mark.parametrize(
    "name",
    [
        "PARTICIPANT_TYPE",
        "RESOURCE_TYPE",
        "PROXIMITY",
        "Participant",
        "Location",
        "Resource",
    ],
)
def test_public_names_importable(name):
    """All RFC 9073 public names are importable from the top-level package."""
    import icalendar

    assert hasattr(icalendar, name)


def test_reltype_snooze():
    """RELTYPE.SNOOZE is defined per :rfc:`9074#section-7.1`."""
    assert RELTYPE.SNOOZE == "SNOOZE"


@pytest.mark.parametrize(
    ("prop_cls", "value"),
    [
        (vCalAddress, "mailto:speaker@example.com"),
        (vUri, "https://example.com/cal"),
    ],
)
def test_order_parameter_on_prop_types(prop_cls, value):
    """ORDER parameter is accessible on multi-instance property types per :rfc:`9073#section-5.1`."""
    prop = prop_cls(value)
    prop.ORDER = 1
    assert prop.ORDER == 1


@pytest.mark.parametrize(
    ("prop_cls", "value"),
    [
        (vCalAddress, "mailto:speaker@example.com"),
        (vUri, "https://example.com/cal"),
    ],
)
def test_derived_parameter_on_prop_types(prop_cls, value):
    """DERIVED parameter is accessible on multi-instance property types per :rfc:`9073#section-5.3`."""
    prop = prop_cls(value)
    prop.DERIVED = True
    assert prop.DERIVED is True


def test_order_validation():
    """ORDER parameter rejects values less than 1 per :rfc:`9073#section-5.1`."""
    t = vText("test")
    with pytest.raises((ValueError, TypeError)):
        t.ORDER = 0


def test_event_participants_accessor(events):
    """Event.participants returns typed Participant instances per :rfc:`9073#section-7.1`."""
    event = events.rfc_9073_participant
    assert len(event.participants) == 1
    assert isinstance(event.participants[0], Participant)


def test_event_locations_accessor(events):
    """Event.locations returns typed Location instances per :rfc:`9073#section-7.2`."""
    event = events.rfc_9073_vlocation
    assert len(event.locations) == 1
    assert isinstance(event.locations[0], Location)


def test_event_resources_accessor(events):
    """Event.resources returns typed Resource instances per :rfc:`9073#section-7.3`."""
    event = events.rfc_9073_vresource
    assert len(event.resources) == 1
    assert isinstance(event.resources[0], Resource)


def test_participant_type_accessor(events):
    """Participant.participant_type returns PARTICIPANT_TYPE enum per :rfc:`9073#section-6.2`."""
    p = events.rfc_9073_participant.participants[0]
    assert p.participant_type == PARTICIPANT_TYPE.ACTIVE


def test_participant_calendar_address(events):
    """Participant.calendar_address returns vCalAddress per :rfc:`9073#section-6.4`."""
    p = events.rfc_9073_participant.participants[0]
    assert isinstance(p.calendar_address, vCalAddress)
    assert "guido@pycon.example.com" in str(p.calendar_address)


def test_location_in_participant(events):
    """VLOCATION nested inside PARTICIPANT is parsed per :rfc:`9073#section-7.1`."""
    p = events.rfc_9073_participant.participants[0]
    assert len(p.locations) == 1
    assert isinstance(p.locations[0], Location)


def test_event_locations_excludes_participant_locations(events):
    """Event.locations returns only direct VLOCATION children, not those inside PARTICIPANT.

    :rfc:`9073#section-7.2` defines VLOCATION as a property of the event itself.
    A VLOCATION inside a PARTICIPANT describes the participant's location, not
    the event's.
    """
    event = events.rfc_9073_participant
    # This event has one VLOCATION inside its PARTICIPANT, but no direct VLOCATION.
    assert len(event.locations) == 0


def test_location_name_accessor(events):
    """Location.location_name returns the NAME property per :rfc:`9073#section-7.2`."""
    loc = events.rfc_9073_vlocation.locations[0]
    assert loc.location_name == "Hydrogen Line Hackerspace Observatory"


def test_resource_type_accessor(events):
    """Resource.resource_type returns RESOURCE_TYPE enum per :rfc:`9073#section-7.3`."""
    res = events.rfc_9073_vresource.resources[0]
    assert res.resource_type == RESOURCE_TYPE.PROJECTOR


def test_alarm_proximity_typed(events):
    """Alarm.proximity returns PROXIMITY enum per :rfc:`9074#section-8.1`."""
    alarm = events.rfc_9074_example_proximity.subcomponents[0]
    assert alarm.proximity == PROXIMITY.DEPART


def test_location_in_alarm_registered(events):
    """VLOCATION inside VALARM parses as a Location instance per :rfc:`9074#section-8`."""
    alarm = events.rfc_9074_example_proximity.subcomponents[0]
    assert isinstance(alarm.subcomponents[0], Location)


def test_order_round_trip(events):
    """ORDER parameter round-trips through parse and serialize per :rfc:`9073#section-5.1`."""
    from icalendar import Calendar

    event = events.rfc_9073_order_parameter
    cal = Calendar()
    cal.add_component(event)
    reparsed = Calendar.from_ical(cal.to_ical())
    revent = reparsed.events[0]
    cats = revent.get("CATEGORIES")
    if isinstance(cats, list):
        orders = [int(c.params.get("ORDER", 0)) for c in cats]
    else:
        orders = [int(cats.params.get("ORDER", 0))] if cats else []
    assert 1 in orders
    assert 2 in orders


def test_derived_round_trip():
    """DERIVED parameter round-trips through parse and serialize per :rfc:`9073#section-5.3`."""
    from icalendar import Calendar, Event

    event = Event()
    addr = vCalAddress("mailto:speaker@example.com")
    addr.DERIVED = True
    event.add("ATTENDEE", addr)
    cal = Calendar()
    cal.add_component(event)
    reparsed = Calendar.from_ical(cal.to_ical())
    attendee = reparsed.events[0].get("ATTENDEE")
    assert attendee.params.get("DERIVED") == "TRUE"


def test_participant_type_enum_values():
    """PARTICIPANT_TYPE enum has all IANA-registered values from :rfc:`9073#section-11.2.1`."""
    assert PARTICIPANT_TYPE.ACTIVE == "ACTIVE"
    assert PARTICIPANT_TYPE.INACTIVE == "INACTIVE"
    assert PARTICIPANT_TYPE.SPONSOR == "SPONSOR"
    assert PARTICIPANT_TYPE.CONTACT == "CONTACT"
    assert PARTICIPANT_TYPE.BOOKING_CONTACT == "BOOKING-CONTACT"
    assert PARTICIPANT_TYPE.EMERGENCY_CONTACT == "EMERGENCY-CONTACT"
    assert PARTICIPANT_TYPE.PUBLICITY_CONTACT == "PUBLICITY-CONTACT"
    assert PARTICIPANT_TYPE.PLANNER_CONTACT == "PLANNER-CONTACT"
    assert PARTICIPANT_TYPE.PERFORMER == "PERFORMER"
    assert PARTICIPANT_TYPE.SPEAKER == "SPEAKER"


def test_resource_type_enum_values():
    """RESOURCE_TYPE enum has all IANA-registered values from :rfc:`9073#section-11.2.2`."""
    assert RESOURCE_TYPE.ROOM == "ROOM"
    assert RESOURCE_TYPE.PROJECTOR == "PROJECTOR"
    assert RESOURCE_TYPE.REMOTE_CONFERENCE_AUDIO == "REMOTE-CONFERENCE-AUDIO"
    assert RESOURCE_TYPE.REMOTE_CONFERENCE_VIDEO == "REMOTE-CONFERENCE-VIDEO"
