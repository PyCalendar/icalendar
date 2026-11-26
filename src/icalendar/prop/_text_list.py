"""Shared representation of a property with multiple TEXT values."""

from collections.abc import Iterable, Iterator
from typing import Any, ClassVar
from xml.etree.ElementTree import Element

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser.property import split_on_unescaped_comma
from icalendar.parser.xcal.base import XCalParser
from icalendar.parser.xcal.wrapper import from_xcal_wrapper
from icalendar.parser_tools import to_unicode
from icalendar.prop.text import vText


class TextList:
    """One iCalendar property containing a list of TEXT values."""

    default_value: ClassVar[str] = "TEXT"
    params: Parameters

    def __init__(
        self, values: Iterable[str] | str, /, params: dict[str, Any] | None = None
    ) -> None:
        """Create a property from its text values.

        Parameters:
            values: A single string or an iterable of individual values.
            params: The iCalendar property parameters.

        Example:
            >>> from icalendar import vLocationType
            >>> vLocationType("hotel").ical_value
            ['hotel']
        """
        if isinstance(values, str) or not isinstance(values, Iterable):
            values = [values]
        self._values: list[vText | str] = [vText(value) for value in values]
        self.params = Parameters(params)

    def __iter__(self) -> Iterator[vText | str]:
        return iter(self._values)

    @property
    def values(self) -> list[str]:
        """The mutable list of TEXT values in this property."""
        return self._values

    def __eq__(self, other: object) -> bool:
        """Compare the text values.

        :meta private:
        """
        if isinstance(other, TextList):
            return self._values == other._values
        if isinstance(other, list):
            return self._values == other
        return NotImplemented

    def __hash__(self) -> int:
        """Hash the text values.

        :meta private:
        """
        return hash(tuple(self._values))

    def __repr__(self) -> str:
        """String representation.

        :meta private:
        """
        return f"{self.__class__.__name__}({self._values}, params={self.params})"

    @property
    def ical_value(self) -> list[str]:
        """The individual values as strings."""
        return [str(value) for value in self._values]

    def to_ical(self) -> bytes:
        return b",".join(
            value.to_ical() if hasattr(value, "to_ical") else vText(value).to_ical()
            for value in self._values
        )

    @staticmethod
    def from_ical(ical: list[str] | str | bytes) -> list[str]:
        r"""Read the items of an iCalendar TEXT list.

        Parameters:
            ical: An encoded TEXT value or a list of unescaped items.

        Returns:
            The individual text values.

        Example:
            >>> from icalendar import vLocationType
            >>> vLocationType.from_ical(r"hotel\,restaurant,office")
            ['hotel,restaurant', 'office']
        """
        if isinstance(ical, list):
            return ical
        return split_on_unescaped_comma(to_unicode(ical))

    @classmethod
    def from_ical_list(cls, raw_value: str) -> Self:
        """Construct one property from the comma-separated values on a content line."""
        return cls(cls.from_ical(raw_value))

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """Serialize the property to jCal.

        Parameters:
            name: The jCal property name.

        Returns:
            The property array with a separate entry for each value.

        Example:
            >>> from icalendar import vLocationType
            >>> vLocationType(["hotel", "restaurant"]).to_jcal("location-type")
            ['location-type', {}, 'text', 'hotel', 'restaurant']
        """
        result = [name, self.params.to_jcal(), self.VALUE.lower()]
        result.extend(map(str, self._values))
        if not self._values:
            result.append("")
        return result

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~icalendar.error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        for index, value in enumerate(jcal_property[3:], start=3):
            JCalParsingError.validate_value_type(value, str, cls, index)
        return cls(jcal_property[3:], Parameters.from_jcal_property(jcal_property))

    def to_xcal(self, element: Element) -> None:
        """Write one xCal text element per value.

        Parameters:
            element: The property element that receives the parameters and values.

        Example:
            >>> from xml.etree.ElementTree import Element
            >>> from icalendar import vCategory
            >>> element = Element("categories")
            >>> vCategory(["Work", "Travel"]).to_xcal(element)
            >>> [child.text for child in element.findall("text")]
            ['Work', 'Travel']
        """
        self.params.to_xcal(element)
        for value in self._values:
            if not isinstance(value, vText):
                value = vText(value)
            value.to_xcal(element)

    @classmethod
    @from_xcal_wrapper
    def from_xcal(cls, parser: XCalParser, params: Parameters) -> Self:
        """Parse xCal according to :rfc:`6321`.

        Parameters:
            parser: Required. The xCal to parse or a parser.
            params: Required. The parameters of the xCal element.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """
        elements = parser.parse_tags(cls.default_value)
        return cls([element.get_xsd_string() for element in elements], params=params)
