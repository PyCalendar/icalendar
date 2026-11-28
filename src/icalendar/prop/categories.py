"""CATEGORIES property values from :rfc:`5545`."""

from icalendar.compatibility import Self
from icalendar.parser_tools import to_unicode
from icalendar.prop._text_list import TextList
from icalendar.prop.text import vText


class vCategory(TextList):
    """The values of the CATEGORIES property.

    Parameters:
        values: Required. A single category name or an iterable of category names.
        params: Optional iCalendar parameters for this CATEGORIES property.
    """

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

        The component parser calls :meth:`from_ical_list`, which
        already splits the CATEGORIES property into a list of unescaped
        category strings. New code should therefore pass a list of strings.

        Passing a single comma-separated string is supported only for
        backwards compatibility with older parsing code and is considered
        legacy behavior.

        Parameters:
            ical: A list of category strings (preferred), or a single comma-separated
                string from a legacy caller.

        Returns:
            A list of category strings.
        """
        if isinstance(ical, list):
            # Already split by the caller
            return ical
        # Legacy: simple comma split (no escaping handled)
        ical = to_unicode(ical)
        return ical.split(",")

    def __hash__(self) -> int:
        """Hash of the vCategory object.

        :meta private:
        """
        return hash(tuple(self.cats))

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vCategory."""
        return [cls(["HOME", "COSY"])]


__all__ = ["vCategory"]
