"""The VLOCATION component from :rfc:`9073#section-7.2`."""

import uuid
from collections.abc import Iterable, Iterator, MutableSequence, Sequence
from contextlib import contextmanager
from datetime import date

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    PropertyListView,
    create_single_property,
    description_property,
)
from icalendar.compatibility import Self
from icalendar.error import InvalidCalendar
from icalendar.prop import vGeo, vLocationType

from .component import Component


class Location(Component):
    """A venue, parking area, or other location associated with a calendar component."""

    name = "VLOCATION"
    required = ("UID",)
    singletons = ("UID", "NAME", "DESCRIPTION", "GEO", "LOCATION-TYPE")

    @property
    def location_name(self) -> str | None:
        """The display name of the location, or None if NAME is absent."""
        name = self.get("NAME")
        if isinstance(name, list):
            raise InvalidCalendar("Multiple NAME defined.")
        if name is not None and not isinstance(name, str):
            raise InvalidCalendar("NAME must contain a TEXT value.")
        return name

    @location_name.setter
    def location_name(self, value: str | None) -> None:
        if value is None:
            del self.location_name
        else:
            self["NAME"] = self._encode("NAME", value)

    @location_name.deleter
    def location_name(self) -> None:
        self.pop("NAME", None)

    description = description_property
    geo = create_single_property(
        "GEO",
        "ical_value",
        (tuple,),
        tuple[float, float],
        "The latitude and longitude of the location, in that order.",
        vProp=vGeo,
    )

    @property
    def location_types(self) -> MutableSequence[str] | None:
        """The types of this location, or None if LOCATION-TYPE is absent.

        Assign one type or a sequence of types. Removing the last type removes
        the property.

        Raises:
            ~icalendar.error.InvalidCalendar: If LOCATION-TYPE is repeated or
                has an incompatible value type.
        """
        view = _LocationTypes(self, "LOCATION-TYPE")
        return view if view._stored_values() is not None else None

    @location_types.setter
    def location_types(self, values: Sequence[str] | None) -> None:
        _LocationTypes(self, "LOCATION-TYPE").replace_with(values)

    @location_types.deleter
    def location_types(self) -> None:
        self.pop("LOCATION-TYPE", None)

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
            description: The :attr:`description` of the location.
            geo: The :attr:`geo` coordinates as (latitude, longitude).
            location_types: One type or a sequence of :attr:`location_types`.
            name: The :attr:`location_name` displayed to users.
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


class _LocationTypes(PropertyListView):
    """Edit the TEXT values inside a single LOCATION-TYPE property.

    :meta private:
    """

    def _stored_values(self) -> list[str] | None:
        prop = self._component.get(self._name)
        if prop is None:
            return None
        if isinstance(prop, list):
            raise InvalidCalendar("Multiple LOCATION-TYPE defined.")
        if isinstance(prop, str) and getattr(prop, "default_value", "TEXT") == "TEXT":
            params = getattr(prop, "params", None)
            if params is None or params.value in (None, "TEXT"):
                return [prop]
        values = getattr(prop, "values", None)
        if not isinstance(values, list):
            raise InvalidCalendar("LOCATION-TYPE must contain a TEXT list.")
        return values

    @contextmanager
    def _values(self) -> Iterator[list[str]]:
        prop = self._component.get(self._name)
        stored = self._stored_values()
        items = stored.copy() if stored is not None else []
        yield items
        if items == stored:
            return
        if not items:
            self.clear()
        elif stored is None or isinstance(prop, str):
            self._component[self._name] = vLocationType(
                items, getattr(prop, "params", None)
            )
        else:
            stored[:] = vLocationType(items).values

    def __len__(self) -> int:
        return len(self._stored_values() or ())

    def __iter__(self) -> Iterator[str]:
        return iter(self._stored_values() or ())

    def extend(self, values: Iterable[str]) -> None:
        with self._values() as items:
            items.extend(values)

    def replace_with(self, values: Sequence[str] | None) -> None:
        if values is None:
            self.clear()
            return
        if not isinstance(values, Sequence) or isinstance(
            values, (bytes, bytearray, memoryview)
        ):
            raise TypeError("LOCATION-TYPE requires a string or a sequence of strings.")
        if not values and not isinstance(values, str):
            self.clear()
            return
        if isinstance(values, _LocationTypes) and values._component is self._component:
            return
        self._component[self._name] = vLocationType(values)


__all__ = ["Location"]
