"""Partial support for RFC 9073: VLOCATION and LOCATION-TYPE."""

import pytest

from icalendar import (
    Calendar,
    Component,
    Event,
    Location,
    Todo,
    vCategory,
    vGeo,
    vLocationType,
    vText,
)
from icalendar.cal import Location as CalLocation
from icalendar.parser.ical import ComponentIcalParser
from icalendar.prop import vBroken, vUnknown


@pytest.mark.parametrize("name", ["VLOCATION", "vlocation"])
def test_location_is_registered(component_factory, name):
    """Both public imports and the parser factory use the dedicated class."""
    assert component_factory.get_component_class(name) is Location is CalLocation


def test_minimal_location():
    """A UID alone is sufficient to represent a location."""
    data = b"BEGIN:VLOCATION\r\nUID:venue@example.com\r\nEND:VLOCATION\r\n"
    location = Component.from_ical(data)
    assert isinstance(location, Location)
    assert location.name == "VLOCATION"
    assert location.uid == "venue@example.com"
    assert isinstance(location["UID"], vText)
    assert location.to_ical() == data


def test_new_location_defaults(test_uid):
    location = Location.new()
    assert location.uid == test_uid
    assert location.location_name is None
    assert location.description is None
    assert location.geo is None
    assert location.location_types is None
    assert list(location) == ["UID"]


@pytest.mark.parametrize("parent_class", [Event, Todo])
def test_add_multiple_locations(parent_class):
    """Each parent keeps distinct locations and its traditional LOCATION text."""
    parent = parent_class()
    parent.add("location", "Conference venue")
    for uid, name, types in [
        ("hotel@example.com", "Central Hotel", ["hotel", "restaurant"]),
        ("parking@example.com", "Car park", ["parking"]),
    ]:
        location = Location.new(uid=uid, name=name, location_types=types)
        parent.add_component(location)

    encoded = parent.to_ical()
    assert b"LOCATION-TYPE:hotel,restaurant\r\n" in encoded
    assert encoded.count(b"LOCATION-TYPE:") == 2
    restored = parent_class.from_ical(encoded)
    assert restored["LOCATION"] == "Conference venue"
    assert [location.uid for location in restored.walk("VLOCATION")] == [
        "hotel@example.com",
        "parking@example.com",
    ]
    assert all(isinstance(location, Location) for location in restored.subcomponents)
    assert restored == parent


def test_parse_locations(calendars):
    """Both eager and lazy calendars preserve locations and their properties."""
    calendar = calendars.rfc_9073_locations
    locations = calendar.walk("VLOCATION")
    assert [location.uid for location in locations] == [
        "hotel@example.com",
        "parking@example.com",
        "office@example.com",
        "restaurant@example.com",
    ]
    for parent_name in ("VEVENT", "VTODO"):
        children = calendar.walk(parent_name)[0].subcomponents
        assert len(children) == 2
        assert all(isinstance(child, Location) for child in children)

    hotel = locations[0]
    assert isinstance(hotel["NAME"], vText)
    assert hotel.location_name == "Hotel Sol, Centro"
    assert hotel["NAME"].params["LANGUAGE"] == "pt-BR"
    assert isinstance(hotel["DESCRIPTION"], vText)
    assert hotel.description == "Recepção no térreo.\nUse a entrada principal."
    assert isinstance(hotel["GEO"], vGeo)
    assert hotel.geo == (-22.97, -43.23)
    assert isinstance(hotel["LOCATION-TYPE"], vLocationType)
    assert hotel.location_types == ["hotel", "restaurant"]
    assert str(hotel["X-ENTRANCE"]) == r"North\, side"
    assert Calendar.from_ical(calendar.to_ical()) == calendar


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
def test_location_format_conversion(calendars, format_name):
    """The existing jCal and xCal converters preserve locations and text lists."""
    calendar = calendars.rfc_9073_locations
    if format_name == "jcal":
        restored = Calendar.from_jcal(calendar.to_jcal())
    else:
        restored = Calendar.from_xcal(calendar.to_xcal())[0]
    locations = restored.walk("VLOCATION")
    assert len(locations) == 4
    assert all(isinstance(location, Location) for location in locations)
    assert isinstance(locations[0]["LOCATION-TYPE"], vLocationType)
    assert list(locations[0]["LOCATION-TYPE"]) == ["hotel", "restaurant"]
    assert locations[0]["NAME"].params["LANGUAGE"] == "pt-BR"
    assert locations[0]["GEO"].ical_value == (-22.97, -43.23)
    assert restored == calendar


@pytest.mark.parametrize(
    ("component_class", "property_name", "value_class"),
    [(Location, "LOCATION-TYPE", vLocationType), (Event, "CATEGORIES", vCategory)],
)
@pytest.mark.parametrize("value_parameter", ["", ";VALUE=TEXT"])
@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("hotel", ["hotel"]),
        ("hotel,restaurant", ["hotel", "restaurant"]),
        (r"hotel\,restaurant,office", ["hotel,restaurant", "office"]),
        (r"room\\,restaurant", ["room\\", "restaurant"]),
        (
            r"café\,terrace,http://example.com/type",
            ["café,terrace", "http://example.com/type"],
        ),
        ("hotel,\r\n restaurant", ["hotel", "restaurant"]),
    ],
)
def test_parse_text_lists(
    component_class, property_name, value_class, value_parameter, raw_value, expected
):
    """Split raw text before unescaping, including folded lines and parameters."""
    source = (
        f"BEGIN:{component_class.name}\r\n"
        "UID:place@example.com\r\n"
        f'{property_name}{value_parameter};X-REF="https://example.com/a:b":{raw_value}\r\n'
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    value = component[property_name]
    assert isinstance(value, value_class)
    assert list(value) == expected
    assert value.params["X-REF"] == "https://example.com/a:b"
    restored = component_class.from_ical(component.to_ical())
    assert list(restored[property_name]) == expected
    assert restored[property_name].params == value.params


def test_text_list_parser_hooks(component_factory, types_factory):
    """A parser can override either property without intercepting the other."""

    class CustomParser(ComponentIcalParser):
        def handle_categories(self, params, vals, line):
            params["X-HANDLED"] = "categories"
            handled = super().handle_categories(params, vals, line)
            assert handled
            return handled

        def handle_location_type(self, params, vals, line):
            params["X-HANDLED"] = "location-type"
            handled = super().handle_location_type(params, vals, line)
            assert handled
            return handled

    source = (
        "BEGIN:VEVENT\r\n"
        "CATEGORIES:Work,Personal\\,Urgent\r\n"
        "BEGIN:VLOCATION\r\n"
        "UID:place@example.com\r\n"
        "LOCATION-TYPE:hotel,restaurant\r\n"
        "END:VLOCATION\r\n"
        "END:VEVENT\r\n"
    )
    event = CustomParser(source, component_factory, types_factory).parse()[0]
    assert list(event["CATEGORIES"]) == ["Work", "Personal,Urgent"]
    assert event["CATEGORIES"].params["X-HANDLED"] == "categories"
    location_types = event.subcomponents[0]["LOCATION-TYPE"]
    assert list(location_types) == ["hotel", "restaurant"]
    assert location_types.params["X-HANDLED"] == "location-type"


@pytest.mark.parametrize(
    ("component_class", "property_name", "base_type"),
    [
        (Location, "LOCATION-TYPE", vLocationType),
        (Location, "LOCATION-TYPE", vCategory),
        (Event, "CATEGORIES", vCategory),
    ],
)
@pytest.mark.parametrize("value_parameter", ["", ";VALUE=TEXT"])
def test_text_list_subclasses(
    component_factory,
    types_factory,
    component_class,
    property_name,
    base_type,
    value_parameter,
):
    """Custom text-list types retain escaped commas, parameters and their class."""

    class CustomTextList(base_type):
        @classmethod
        def get_value_from_content_line(cls, line):
            return line.raw_parts()[2].removeprefix("test:")

    types_factory.types_map = types_factory.types_map.copy()
    types_factory["custom-list"] = CustomTextList
    types_factory.types_map[property_name] = "custom-list"
    source = (
        f"BEGIN:{component_class.name}\r\n"
        f"{property_name}{value_parameter};X-NOTE=custom:test:hotel,restaurant\\,terrace\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = ComponentIcalParser(source, component_factory, types_factory).parse()[0]
    value = component[property_name]
    assert isinstance(value, CustomTextList)
    assert list(value) == ["hotel", "restaurant,terrace"]
    assert value.params["X-NOTE"] == "custom"
    restored = ComponentIcalParser(
        component.to_ical(), component_factory, types_factory
    ).parse()[0]
    assert isinstance(restored[property_name], CustomTextList)
    assert list(restored[property_name]) == list(value)
    assert restored[property_name].params == value.params


@pytest.mark.parametrize("types", ["hotel", ["hotel", "restaurant"]])
def test_add_location_types(types):
    """A string or list produces one property with the appropriate values."""
    location = Location()
    location.add("location-type", types, parameters={"VALUE": "TEXT"})
    assert isinstance(location["LOCATION-TYPE"], vLocationType)
    encoded = location.to_ical()
    expected = [types] if isinstance(types, str) else types
    assert encoded.count(b"LOCATION-TYPE;") == 1
    assert list(Location.from_ical(encoded)["LOCATION-TYPE"]) == expected


@pytest.mark.parametrize("types", ["hotel", ("hotel", "restaurant")])
def test_edit_location_types(types):
    location = Location.new(location_types=types)
    location["LOCATION-TYPE"].params["X-NOTE"] = "venue"
    location.location_types.append("parking")
    restored = Location.from_ical(location.to_ical())
    expected = ["hotel"] if isinstance(types, str) else list(types)
    assert restored.location_types == [*expected, "parking"]
    assert restored["LOCATION-TYPE"].params["X-NOTE"] == "venue"


def test_replace_and_remove_location_properties():
    location = Location.from_ical(
        "BEGIN:VLOCATION\r\nUID:venue\r\nNAME;LANGUAGE=en:Old name\r\n"
        "LOCATION-TYPE:hotel,restaurant\r\nGEO:48.2;16.37\r\nEND:VLOCATION\r\n"
    )
    location.location_name = "Central Hotel"
    location.geo = (0, 0)
    location.location_types = "office"
    assert location.name == "VLOCATION"
    assert location["NAME"] == "Central Hotel"
    assert location["GEO"].ical_value == (0, 0)
    assert location["LOCATION-TYPE"] == ["office"]
    location.location_name = None
    del location.geo
    location.location_types = None
    assert list(location) == ["UID"]


@pytest.mark.parametrize(
    ("component_class", "property_name"),
    [(Location, "LOCATION-TYPE"), (Event, "CATEGORIES")],
)
@pytest.mark.parametrize(
    ("line", "expected"),
    [(r";X-A=\::", [":"]), (";X-NOTE=room", [""])],
)
def test_text_list_value_separator(component_class, property_name, line, expected):
    component = component_class.from_ical(
        f"BEGIN:{component_class.name}\r\n{property_name}{line}\r\nEND:{component_class.name}\r\n"
    )
    assert component.decoded(property_name) == expected


def test_categories_legacy_string_decoder():
    assert vCategory.from_ical(r"Work\,Personal,Travel") == [
        "Work\\",
        "Personal",
        "Travel",
    ]


def test_registered_list_decoder(component_factory, types_factory):
    class RawListText(vText):
        @classmethod
        def from_ical_list(cls, raw_value):
            return cls(raw_value)

    types_factory["location-type"] = RawListText
    source = "BEGIN:VLOCATION\r\nLOCATION-TYPE:hotel\\,terrace,restaurant\r\nEND:VLOCATION\r\n"
    location = ComponentIcalParser(source, component_factory, types_factory).parse()[0]
    assert isinstance(location["LOCATION-TYPE"], RawListText)
    assert location["LOCATION-TYPE"] == r"hotel\,terrace,restaurant"


def test_text_list_read_error_preserves_raw_value(component_factory, types_factory):
    class InvalidCategory(vCategory):
        @classmethod
        def get_value_from_content_line(cls, _line):
            raise ValueError("invalid category list")

    types_factory["categories"] = InvalidCategory
    source = "BEGIN:VEVENT\r\nCATEGORIES;LANGUAGE=en:Work\\,Personal,Travel\r\nEND:VEVENT\r\n"
    event = ComponentIcalParser(source, component_factory, types_factory).parse()[0]
    value = event["CATEGORIES"]
    assert isinstance(value, vBroken)
    assert str(value) == r"Work\,Personal,Travel"
    assert value.params["LANGUAGE"] == "en"


def test_location_type_from_jcal_text():
    jcal = ["location-type", {"x-note": "venue"}, "text", "hotel", "restaurant"]
    value = vText.from_jcal(jcal)
    assert isinstance(value, vLocationType)
    assert list(value) == ["hotel", "restaurant"]
    assert value.params["X-NOTE"] == "venue"
    assert value.to_jcal("location-type") == jcal


@pytest.mark.parametrize(
    ("component_class", "property_name"),
    [(Location, "LOCATION-TYPE"), (Event, "CATEGORIES")],
)
def test_unknown_value_is_preserved(component_class, property_name):
    """An explicit UNKNOWN value must bypass text-list processing."""
    raw_value = r"hotel\,restaurant,office\nannex"
    source = (
        f"BEGIN:{component_class.name}\r\n"
        f"{property_name};VALUE=UNKNOWN:{raw_value}\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    assert isinstance(component[property_name], vUnknown)
    assert str(component[property_name]) == raw_value
    assert component.to_ical() == source.encode()


@pytest.mark.parametrize("component_class", [Location, Calendar])
def test_name_is_text(component_class):
    """NAME is decoded as TEXT, including its use in RFC 7986 calendars."""
    source = (
        f"BEGIN:{component_class.name}\r\n"
        "NAME;LANGUAGE=pt-BR:Hotel Sol\\, Centro\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    assert isinstance(component["NAME"], vText)
    assert component["NAME"] == "Hotel Sol, Centro"
    assert component["NAME"].params["LANGUAGE"] == "pt-BR"


def test_location_text_round_trip():
    """Text escaping, Unicode and line folding use the existing serializers."""
    location = Location.new(
        uid="venue@example.com",
        name="São Paulo, Centro " * 10,
        description="Entrance; east\\west\nSecond floor",
        geo=(-23.55, -46.63),
        location_types=["café,terrace", "room\\A"],
    )
    encoded = location.to_ical()
    assert b"\r\n " in encoded
    restored = Location.from_ical(encoded)
    assert restored["NAME"] == location["NAME"]
    assert restored["DESCRIPTION"] == location["DESCRIPTION"]
    assert restored.geo == (-23.55, -46.63)
    assert restored.location_types == ["café,terrace", "room\\A"]
    assert restored == location


def test_invalid_geo():
    """Malformed coordinates follow the existing vGeo error handling."""
    with pytest.raises(ValueError, match="float;float"):
        Location.from_ical("BEGIN:VLOCATION\r\nGEO:invalid\r\nEND:VLOCATION\r\n")
