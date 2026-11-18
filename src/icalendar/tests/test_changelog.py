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
    errors = []
    if not NEWS_FILENAME.fullmatch(path.name):
        errors.append(f"invalid filename {path.name!r}; expected '<issue>.<type>[.<n>]'")
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


@pytest.fixture(params=sorted(NEWS_DIR.iterdir()) if NEWS_DIR.is_dir() else [])
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
