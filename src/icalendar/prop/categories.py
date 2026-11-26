"""CATEGORIES property values from :rfc:`5545`."""

from icalendar.compatibility import Self
from icalendar.parser_tools import to_unicode
from icalendar.prop._text_list import TextList
from icalendar.prop.text import vText


class vCategory(TextList):
    """The values of the CATEGORIES property."""

    @property
    def _values(self) -> list[vText | str]:
        """Keep the public ``cats`` attribute as the backing list."""
        return self.cats

    @_values.setter
    def _values(self, values: list[vText | str]) -> None:
        self.cats = values

    @classmethod
    def from_ical_list(cls, raw_value: str) -> Self:
        """Use TEXT escaping for content lines. Direct string callers use the legacy decoder."""
        return cls(super().from_ical(raw_value))

    @staticmethod
    def from_ical(ical: list[str] | str | bytes) -> list[str]:
        """Parse a CATEGORIES value from iCalendar format.

        A list contains individual, unescaped categories. A comma-separated
        string uses the legacy splitting rules. The component parser reads
        the escaped TEXT list with :meth:`from_ical_list`.

        Parameters:
            ical: A list of category strings or a legacy comma-separated value.

        Returns:
            A list of category strings.
        """
        if isinstance(ical, list):
            return ical
        # Legacy: simple comma split (no escaping handled)
        ical = to_unicode(ical)
        return ical.split(",")

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vCategory."""
        return [cls(["HOME", "COSY"])]


__all__ = ["vCategory"]
