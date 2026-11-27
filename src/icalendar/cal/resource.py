""":rfc:`9073` Resource component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.attr import (
    description_property,
    single_string_enum_property,
    single_string_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.enums import RESOURCE_TYPE

if TYPE_CHECKING:
    from icalendar.prop import vGeo


class Resource(Component):
    """A VRESOURCE calendar component from :rfc:`9073#section-7.3`.

    This component provides structured resource information for a calendar
    component. It may appear inside :class:`~icalendar.cal.event.Event`,
    :class:`~icalendar.cal.free_busy.FreeBusy`,
    :class:`~icalendar.cal.journal.Journal`,
    :class:`~icalendar.cal.participant.Participant`, or
    :class:`~icalendar.cal.todo.Todo` per :rfc:`9074#section-8`. Multiple
    instances are allowed.

    Example:

        .. code-block:: pycon

            >>> from icalendar import Resource, RESOURCE_TYPE
            >>> res = Resource()
            >>> res.resource_name = "Projector"
            >>> res.resource_type = RESOURCE_TYPE.PROJECTOR
            >>> res.resource_type
            <RESOURCE_TYPE.PROJECTOR: 'PROJECTOR'>
    """

    name = "VRESOURCE"
    singletons = ("NAME", "DESCRIPTION", "GEO", "RESOURCE-TYPE", "UID")

    resource_name = single_string_property(
        "NAME",
        """The display name of this resource per :rfc:`7986#section-5.1`.

        Returns:
            The value of the NAME property when set, or the empty string when
            no NAME property is set.
        """,
    )

    description = description_property

    uid = uid_property

    resource_type = single_string_enum_property(
        "RESOURCE-TYPE",
        RESOURCE_TYPE,
        None,
        """The type of resource per :rfc:`9073#section-6.3`.

        IANA-registered values are defined in :rfc:`9073#section-11.2.2`:
        ``ROOM``, ``PROJECTOR``, ``REMOTE-CONFERENCE-AUDIO``, and
        ``REMOTE-CONFERENCE-VIDEO``.

        Returns:
            A :class:`~icalendar.enums.RESOURCE_TYPE` member for
            IANA-registered values, a plain :class:`str` for unknown values, or
            ``None`` when absent.

        """,
        preserve_unknown=True,
    )

    @property
    def geo(self) -> vGeo | None:
        """The geographic position of this resource per :rfc:`5545#section-3.8.1.6`.

        Returns:
            A :class:`~icalendar.prop.geo.vGeo` instance, or ``None`` when
            no GEO property is set.
        """
        return self.get("GEO")


__all__ = ["Resource"]
