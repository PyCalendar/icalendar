""":rfc:`9073` Location component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.attr import (
    description_property,
    single_string_property,
    uid_property,
)
from icalendar.cal.component import Component

if TYPE_CHECKING:
    from icalendar.prop import vGeo


class Location(Component):
    """A VLOCATION calendar component from :rfc:`9073#section-7.2`.

    This component provides structured location information for a calendar
    component.

    It may appear inside :class:`~icalendar.cal.alarm.Alarm`,
    :class:`~icalendar.cal.event.Event`,
    :class:`~icalendar.cal.free_busy.FreeBusy`,
    :class:`~icalendar.cal.journal.Journal`,
    :class:`~icalendar.cal.participant.Participant`, or
    :class:`~icalendar.cal.todo.Todo` per :rfc:`9074#section-8`. Multiple
    instances are allowed.

    Example:

        .. code-block:: pycon

            >>> from icalendar import Location
            >>> loc = Location()
            >>> loc.location_name = "Conference Room A"
            >>> loc.uid = "room-a-uid@example.com"
            >>> str(loc.location_name)
            'Conference Room A'
    """

    name = "VLOCATION"
    singletons = ("NAME", "DESCRIPTION", "GEO", "LOCATION-TYPE", "UID")

    location_name = single_string_property(
        "NAME",
        """The display name of this location per :rfc:`7986#section-5.1`.

        Returns:
            The value of the NAME property when set, or the empty string when
            no NAME property is set.
        """,
    )

    description = description_property

    uid = uid_property

    location_type = single_string_property(
        "LOCATION-TYPE",
        """The raw LOCATION-TYPE value per :rfc:`9073#section-6.1`.

        The property value is a comma-separated list of location type tokens
        from the IANA registry defined in :rfc:`4589#section-3`,
        for example, ``"office,airport"``. This accessor returns the raw
        string. Split on commas to work with individual tokens.

        Returns:
            The value of the LOCATION-TYPE property if set, or the empty string
            when not set.
        """,
    )

    @property
    def geo(self) -> vGeo | None:
        """The geographic position of this location per :rfc:`5545#section-3.8.1.6`.

        Returns:
            A :class:`~icalendar.prop.geo.vGeo` instance, or ``None`` when
            no GEO property is set.
        """
        return self.get("GEO")


__all__ = ["Location"]
