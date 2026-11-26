"""LOCATION-TYPE property values from :rfc:`9073#section-6.1`."""

from icalendar.compatibility import Self
from icalendar.parser.content_line import Contentline
from icalendar.prop._text_list import TextList


class vLocationType(TextList):
    """The types of a location, such as a hotel or restaurant."""

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
