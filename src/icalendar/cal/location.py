"""The VLOCATION component from :rfc:`9073#section-7.2`."""

import uuid
from collections.abc import Iterable, Sequence
from datetime import date

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    create_single_property,
    description_property,
    multi_language_text_property,
)
from icalendar.compatibility import Self
from icalendar.prop import vGeo, vLocationType

from .component import Component


class Location(Component):
    """A venue, parking area, or other location associated with a calendar component."""

    name = "VLOCATION"
    required = ("UID",)
    singletons = ("UID", "NAME", "DESCRIPTION", "GEO", "LOCATION-TYPE")

    location_name = multi_language_text_property(
        "NAME", None, "The display name of the location."
    )
    description = description_property
    geo = create_single_property(
        "GEO",
        "ical_value",
        (tuple,),
        tuple[float, float],
        "The latitude and longitude of the location, in that order.",
        vProp=vGeo,
    )
    location_types = create_single_property(
        "LOCATION-TYPE",
        "values",
        (Sequence,),
        Sequence[str],
        "Assign one type or a sequence of types. The stored TEXT list can be edited in place.",
        vProp=vLocationType,
    )

    @classmethod
    def new(
        cls,
        created: date | None = None,
        comments: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
        last_modified: date | None = None,
        links: LINKS_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        stamp: date | None = None,
        subcomponents: Iterable[Component] | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        geo: tuple[float, float] | None = None,
        location_types: Sequence[str] | None = None,
        uid: str | uuid.UUID | None = None,
    ) -> Self:
        """Create a location with a unique identifier.

        Parameters:
            name: The :attr:`location_name` displayed to users.
            description: The :attr:`description` of the location.
            geo: The :attr:`geo` coordinates as (latitude, longitude).
            location_types: One type or a sequence of :attr:`location_types`.
            uid: The :attr:`uid` of the location. Defaults to a new UUID.

        See :meth:`Component.new <icalendar.cal.component.Component.new>` for the shared component arguments.
        """
        location = super().new(
            created=created,
            comments=comments,
            concepts=concepts,
            last_modified=last_modified,
            links=links,
            refids=refids,
            related_to=related_to,
            stamp=stamp,
            subcomponents=subcomponents,
        )
        location.uid = uid if uid is not None else uuid.uuid4()
        location.location_name = name
        location.description = description
        location.geo = geo
        location.location_types = location_types
        return location


__all__ = ["Location"]
