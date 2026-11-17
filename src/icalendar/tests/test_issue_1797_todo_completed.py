"""Test Todo.COMPLETED and Todo.completed property accessors.

See https://github.com/PyCalendar/icalendar/issues/1797
and RFC 5545 section 3.8.2.1.
"""

from datetime import date, datetime, timezone

from icalendar import Calendar, Event, Journal, Todo
from icalendar.timezone import tzp

UTC = timezone.utc


def test_todo_completed_from_date_example_1():
    """Example 1: COMPLETED:20070501 without explicit VALUE=DATE parameter."""
    cal = Calendar.from_ical(
        """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VTODO
UID:20070313T123432Z-456553@example.com
DTSTAMP:20070313T123432Z
COMPLETED:20070501
SUMMARY:Submit Quebec Income Tax Return for 2006
CLASS:CONFIDENTIAL
CATEGORIES:FAMILY,FINANCE
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR"""
    )
    todo = cal.todos[0]
    expected = tzp.localize_utc(datetime(2007, 5, 1, 0, 0))
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_todo_completed_from_date_example_2():
    """Example 2: COMPLETED;VALUE=DATE:20070501 with VALUE=DATE parameter."""
    cal = Calendar.from_ical(
        """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VTODO
UID:20070313T123432Z-456553@example.com
DTSTAMP:20070313T123432Z
COMPLETED;VALUE=DATE:20070501
SUMMARY:Submit Quebec Income Tax Return for 2006
CLASS:CONFIDENTIAL
CATEGORIES:FAMILY,FINANCE
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR"""
    )
    todo = cal.todos[0]
    expected = tzp.localize_utc(datetime(2007, 5, 1, 0, 0))
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_todo_completed_fixture_date(todos):
    """Load test file from todos fixture and verify COMPLETED date converted to UTC datetime."""
    todo = todos.issue_1797_completed_date
    expected = tzp.localize_utc(datetime(2007, 5, 1, 0, 0))
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_todo_completed_fixture_datetime(todos):
    """Load test file from todos fixture and verify COMPLETED datetime."""
    todo = todos.issue_1797_completed_datetime
    expected = tzp.localize_utc(datetime(2007, 5, 1, 12, 30))
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_todo_completed_getter_setter_deleter():
    """Test getting, setting, and deleting COMPLETED and completed."""
    todo = Todo()
    assert todo.COMPLETED is None
    assert todo.completed is None

    # Set using uppercase COMPLETED with datetime
    completed_dt = datetime(2024, 6, 1, 15, 0, tzinfo=UTC)
    todo.COMPLETED = completed_dt
    assert todo.COMPLETED == completed_dt
    assert todo.completed == completed_dt
    assert b"COMPLETED:20240601T150000Z" in todo.to_ical()

    # Delete using uppercase COMPLETED
    del todo.COMPLETED
    assert todo.COMPLETED is None
    assert todo.completed is None
    assert "COMPLETED" not in todo

    # Set using lowercase completed with date
    completed_date = date(2024, 6, 1)
    todo.completed = completed_date
    assert todo.COMPLETED == tzp.localize_utc(datetime(2024, 6, 1, 0, 0))
    assert todo.completed == tzp.localize_utc(datetime(2024, 6, 1, 0, 0))

    # Set to None clears it
    todo.completed = None
    assert todo.COMPLETED is None
    assert todo.completed is None

    # Delete using lowercase completed
    todo.completed = completed_dt
    del todo.completed
    assert todo.COMPLETED is None
    assert todo.completed is None


def test_todo_new_with_completed():
    """Test creating a Todo using Todo.new(completed=...)."""
    completed_dt = datetime(2024, 7, 10, 10, 0, tzinfo=UTC)
    todo = Todo.new(
        summary="Finish documentation",
        completed=completed_dt,
    )
    assert todo.COMPLETED == completed_dt
    assert todo.completed == completed_dt
    assert b"COMPLETED:20240710T100000Z" in todo.to_ical()


def test_completed_not_present_in_other_components():
    """RFC 5545 defines COMPLETED specifically for VTODO (Section 3.8.2.1)."""
    event = Event()
    journal = Journal()
    assert not hasattr(event, "COMPLETED")
    assert not hasattr(event, "completed")
    assert not hasattr(journal, "COMPLETED")
    assert not hasattr(journal, "completed")
