"""Check that change log entries in the news directory follow the project's format.

See https://icalendar.readthedocs.io/en/latest/contribute/index.html#change-log-requirements
"""

import re
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[3]
NEWS_DIRECTORY = REPOSITORY_ROOT / "news"
DOCS = "https://icalendar.readthedocs.io/en/latest/contribute/index.html#change-log-requirements"

TYPES = (
    "breaking",
    "removal",
    "feature",
    "bugfix",
    "security",
    "documentation",
    "deps",
    "internal",
    "chore",
)
USER_ROLE = re.compile(r":user:`[\w-]+`$")
FILE_NAME = re.compile(rf"^(\d+|\+[\w-]+)\.({'|'.join(TYPES)})(\.\d+)?$")


def news_files() -> list[Path]:
    """Return the change log entries, or an empty list if there is no news directory."""
    if not NEWS_DIRECTORY.is_dir():
        return []
    return sorted(
        path
        for path in NEWS_DIRECTORY.iterdir()
        if path.is_file() and not path.name.startswith(".")
    )


@pytest.fixture(params=news_files(), ids=lambda path: path.name)
def news_file(request) -> Path:
    """Each change log entry, one at a time."""
    return request.param


@pytest.fixture
def news_text(news_file: Path) -> str:
    """The content of the change log entry without surrounding whitespace."""
    return news_file.read_text(encoding="utf-8").strip()


def test_file_name(news_file: Path):
    """The file name is <issue>.<type>, optionally with .<number>, or starts with +."""
    assert FILE_NAME.match(news_file.name), (
        f"news/{news_file.name} has an invalid file name. "
        f"Use <issue number>.<type>, such as 2149.internal or 876.feature.1, "
        f"or +<name>.<type> for entries without an issue. "
        f"Valid types: {', '.join(TYPES)}. See {DOCS}"
    )


def test_one_line(news_file: Path, news_text: str):
    """The entry is written on a single line."""
    assert "\n" not in news_text, (
        f"news/{news_file.name} has more than one line. "
        f"Write the whole entry on a single line. See {DOCS}"
    )


def test_no_leading_dash(news_file: Path, news_text: str):
    """The entry is a sentence, not a list item."""
    assert not news_text.startswith("-"), (
        f"news/{news_file.name} starts with '-'. "
        f"Remove the leading '-' and start with a sentence. See {DOCS}"
    )


def test_ends_with_user_role(news_file: Path, news_text: str):
    """The entry ends with an attribution using the :user: role."""
    assert USER_ROLE.search(news_text), (
        f"news/{news_file.name} must end with :user:`your_github_username`, "
        f"not @your_github_username. See {DOCS}"
    )
