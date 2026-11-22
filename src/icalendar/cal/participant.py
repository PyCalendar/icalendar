""":rfc:`9073` PARTICIPANT component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.attr import (
    description_property,
    single_string_enum_property,
    summary_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.enums import PARTICIPANT_TYPE

if TYPE_CHECKING:
    from icalendar.prop import vCalAddress


class Participant(Component):
    """A PARTICIPANT calendar component from :rfc:`9073#section-7.1`.

    Provides structured participant information for a calendar component.
    May appear inside VEVENT, VTODO, VJOURNAL, or VFREEBUSY.
    Multiple instances are allowed. PARTICIPANT-TYPE is required.

    Example:

        .. code-block:: pycon

            >>> from icalendar import Participant, PARTICIPANT_TYPE
            >>> p = Participant()
            >>> p.participant_type = PARTICIPANT_TYPE.ACTIVE
            >>> p.participant_type
            <PARTICIPANT_TYPE.ACTIVE: 'ACTIVE'>
    """

    name = "PARTICIPANT"
    singletons = (
        "PARTICIPANT-TYPE",
        "CALENDAR-ADDRESS",
        "DESCRIPTION",
        "SUMMARY",
        "UID",
    )
    required = ("PARTICIPANT-TYPE",)

    participant_type = single_string_enum_property(
        "PARTICIPANT-TYPE",
        PARTICIPANT_TYPE,
        None,
        """The type of participant per :rfc:`9073#section-6.2`.

        This property MUST appear exactly once in a PARTICIPANT component.
        Returns a :class:`~icalendar.enums.PARTICIPANT_TYPE` member for
        IANA-registered values, a plain :class:`str` for unknown values,
        or ``None`` when absent.

        IANA-registered values from :rfc:`9073#section-11.2.1`:
        ``ACTIVE``, ``INACTIVE``, ``SPONSOR``, ``CONTACT``,
        ``BOOKING-CONTACT``, ``EMERGENCY-CONTACT``, ``PUBLICITY-CONTACT``,
        ``PLANNER-CONTACT``, ``PERFORMER``, ``SPEAKER``.
        """,
        preserve_unknown=True,
    )

    @property
    def calendar_address(self) -> vCalAddress | None:
        """The scheduling address for this participant per :rfc:`9073#section-6.4`.

        Returns a :class:`~icalendar.prop.cal_address.vCalAddress` instance
        or ``None`` when no CALENDAR-ADDRESS property is present.
        """
        return self.get("CALENDAR-ADDRESS")

    uid = uid_property
    summary = summary_property
    description = description_property

    @property
    def locations(self) -> list:
        """All VLOCATION sub-components of this participant per :rfc:`9073#section-7.2`."""
        return self.walk("VLOCATION")

    @property
    def resources(self) -> list:
        """All VRESOURCE sub-components of this participant per :rfc:`9073#section-7.3`."""
        return self.walk("VRESOURCE")


__all__ = ["Participant"]
