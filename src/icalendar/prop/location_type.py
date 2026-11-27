"""LOCATION-TYPE property values from :rfc:`9073#section-6.1`."""

from collections.abc import Iterable, Sequence

from icalendar.compatibility import Self
from icalendar.parser.content_line import Contentline
from icalendar.prop._text_list import TextList


class vLocationType(TextList):
    """The types of a location, such as a hotel or restaurant.

    Parameters:
        values: Required. A single type name or a non-empty iterable of type names.
        params: Optional iCalendar parameters for this LOCATION-TYPE property.

    Example:
        >>> from icalendar import vLocationType
        >>> vLocationType("hotel").ical_value
        ['hotel']
    """

    @staticmethod
    def _checked_values(values: Iterable[str]) -> Sequence[str]:
        """Require at least one TEXT value for a LOCATION-TYPE property.

        :meta private:
        """
        if isinstance(values, (bytes, bytearray, memoryview)):
            raise TypeError("LOCATION-TYPE requires strings.")
        items = values if isinstance(values, Sequence) else tuple(values)
        if not items:
            raise ValueError("LOCATION-TYPE requires at least one value.")
        if not all(isinstance(item, str) for item in items):
            raise TypeError("LOCATION-TYPE requires strings.")
        return items

    @classmethod
    def get_value_from_content_line(cls, line: Contentline) -> str:
        """Read the raw TEXT list so escaped commas survive until the items are split."""
        raw_value = line.raw_text_list_value()
        return line.raw_parts()[2] if raw_value is None else raw_value

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vLocationType."""
        return [cls(["hotel", "restaurant"])]


__all__ = ["vLocationType"]
