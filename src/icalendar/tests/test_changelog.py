"""Validate Towncrier news fragments.

See https://icalendar.readthedocs.io/en/latest/contribute/index.html#change-log
for filename, formatting, and attribution requirements.
"""

import re
from pathlib import Path

import pytest

NEWS_DIR = Path(__file__).resolve().parents[3] / "news"
NEWS_TYPES = frozenset(
    {
        "breaking",
        "removal",
        "feature",
        "bugfix",
        "security",
        "documentation",
        "deps",
        "internal",
        "chore",
    }
)
NEWS_FILENAME = re.compile(
    rf"(?:\d+|\+[^./]+)\.(?:{'|'.join(sorted(NEWS_TYPES))})(?:\.\d+)?\Z"
)
ATTRIBUTION = re.compile(r"@[-\w]+\Z")


def validate_news_item(path: Path, content: str) -> list[str]:
    """Report all violations of the changelog format for one fragment."""
    errors: list[str] = []
    if not NEWS_FILENAME.fullmatch(path.name):
        errors.append(
            f"invalid filename {path.name!r}; expected '<issue>.<type>[.<n>]'"
        )
    if len(content.splitlines()) != 1:
        errors.append("entry must contain exactly one non-empty line")
    line = content.strip()
    if not line:
        errors.append("entry must not be empty")
    elif line.startswith("-"):
        errors.append("entry must not begin with a hyphen")
    if line and not ATTRIBUTION.search(line):
        errors.append("entry must end with GitHub attribution such as '@username'")
    return errors


# Pre-existing fragments that do not meet the newly documented requirements.
# Keep the exceptions explicit: new fragments must comply with the format.
LEGACY_NEWS_EXCEPTIONS = frozenset(
    {
        "+fix-ruff-link.internal",
        "1011.removal.rst",
        "1158.documentation.1736.rst",
        "1158.documentation.5.rst",
        "1727.documentation.rst",
        "1916.feature.rst",
        "938.chore.1",
    }
)


def news_fragment_paths() -> list[Path]:
    """Find publishable fragments, excluding placeholders and known legacy exceptions."""
    if not NEWS_DIR.is_dir():
        return []
    return sorted(
        path
        for path in NEWS_DIR.iterdir()
        if path.is_file()
        and path.name != ".gitkeep"
        and path.name not in LEGACY_NEWS_EXCEPTIONS
    )


@pytest.fixture(params=news_fragment_paths())
def news_fragment(request: pytest.FixtureRequest) -> tuple[Path, str]:
    """Provide each fragment, skipping the check when news/ is absent or empty."""
    path = request.param
    if not path.is_file():
        pytest.skip("Only changelog fragment files are checked")
    return path, path.read_text(encoding="utf-8")


def test_changelog_format(news_fragment: tuple[Path, str]) -> None:
    """Keep changelog entries publishable and attributed."""
    path, content = news_fragment
    errors = validate_news_item(path, content)
    assert not errors, (
        f"{path.name}: {'; '.join(errors)}. See "
        "https://icalendar.readthedocs.io/en/latest/contribute/index.html#change-log"
    )
