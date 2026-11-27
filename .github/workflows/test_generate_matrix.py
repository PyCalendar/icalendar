"""Test that we get the right output under all conditions.

Run with:

    uv run pytest .github/workflows/test_generate_matrix.py

"""

import pytest
from generate_matrix import generate_matrix

RUNNERS = {"ubuntu-latest", "windows-latest", "macos-latest"}

CASES_ALL = {
    "3.10 (ubuntu-latest)",
    "3.10 (windows-latest)",
    "3.11 (ubuntu-latest)",
    "3.12 (ubuntu-latest)",
    "3.13 (ubuntu-latest)",
    "3.14 (ubuntu-latest)",
    "3.14 (windows-latest)",
    "3.14 (macos-latest)",
    "3.10 (nopytz, macos-latest)",
    "pypy3 (ubuntu-latest)",
}
CASES_MIN = {
    "3.10 (windows-latest)",
    "3.14 (ubuntu-latest)",
    "3.10 (nopytz, macos-latest)",
}
CASES_NO_PYPY = CASES_ALL - {"pypy3 (ubuntu-latest)"}
CASES_0 = set()


@pytest.fixture(
    params=[
        # push runs PyPy on main only; review never runs PyPy
        ("", CASES_ALL, "refs/heads/main", "push"),
        ("", CASES_NO_PYPY, "refs/heads/8.x", "push"),
        ("", CASES_NO_PYPY, "refs/heads/7.x", "push"),
        ("", CASES_NO_PYPY, "refs/heads/release-1", "push"),
        ("", CASES_NO_PYPY, "refs/tags/v8.0.2", "push"),
        ("", CASES_MIN, "refs/heads/pr-branch", "push"),
        # review
        ("changes_requested", CASES_0, "refs/heads/main", "pull_request_review"),
        ("changes_requested", CASES_0, "refs/heads/8.x", "pull_request_review"),
        ("changes_requested", CASES_0, "refs/heads/7.x", "pull_request_review"),
        ("changes_requested", CASES_0, "refs/heads/release-2", "pull_request_review"),
        ("changes_requested", CASES_0, "refs/tags/v8.0.2", "pull_request_review"),
        ("changes_requested", CASES_0, "refs/heads/pr-branch", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/heads/main", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/pull/123/merge", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/heads/8.x", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/heads/7.x", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/heads/release-3", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/tags/v8.0.2", "pull_request_review"),
        ("approved", CASES_NO_PYPY, "refs/heads/pr-branch", "pull_request_review"),
    ],
)
def cases(request):
    """All test cases."""
    return request.param


@pytest.fixture
def arg_pr(cases):
    """The pr event name."""
    return cases[0]


@pytest.fixture
def arg_ref(cases):
    """The branch or tag reference."""
    return cases[2]


@pytest.fixture
def arg_event_name(cases):
    """The GitHub event name."""
    return cases[3]


@pytest.fixture
def expected(cases):
    """All expected case names."""
    return cases[1]


@pytest.fixture
def matrix(arg_ref, arg_pr, arg_event_name):
    """The generated test matrix."""
    matrix = generate_matrix(arg_ref, arg_pr, arg_event_name)
    print("Cases:")
    for case in sorted(matrix["include"], key=lambda case: case["test_name"]):
        print(f"- running\t{case['test_name']}")
    for case in sorted(matrix["skipped"]):
        print(f"- skipped\t{case}")
    return matrix


@pytest.fixture
def skipped_names(matrix):
    """All skipped test cases."""
    return set(matrix["skipped"])


@pytest.fixture
def running_names(matrix):
    """All running test cases"""
    return {case["test_name"] for case in matrix["include"] if not case["skip"]}


def test_event_matches_review_state(cases):
    """Event and review state must pair as GitHub delivers them.

    Reviews never arrive via push, while other events
    stay free for future rows.
    """
    review, _, _, event = cases
    assert not (review and event == "push")


def test_count_test_runs(running_names, expected):
    """Check which values we get."""
    assert running_names == expected, (
        f"Expected {len(expected)} test runs, got {len(running_names)}"
    )


def test_running_is_not_skipped(running_names, skipped_names):
    """Running means not skipped."""
    assert running_names.isdisjoint(skipped_names)


def test_all_cases_are_always_included(running_names, skipped_names, matrix):
    """The matrix always needs to be complete or we might wait for required checks."""
    assert running_names | skipped_names == CASES_ALL
    all_in_matrix = {case["test_name"] for case in matrix["include"]}
    assert all_in_matrix == CASES_ALL


@pytest.mark.parametrize(
    "attribute",
    [
        "test_name",
        "python_version",
        "runner",
        "skip",
        "test_command",
    ],
)
def test_parameters_are_present(matrix, attribute):
    for case in matrix["include"]:
        assert attribute in case, f"Missing {attribute} in {case}"


def test_runners_are_supported(matrix):
    """Only runners that exist are used, so no job waits for a typo."""
    for case in matrix["include"]:
        assert case["runner"] in RUNNERS, case


def test_skipped_jobs_run_on_ubuntu(matrix):
    """Skipped jobs still start a runner: do not spend macOS or Windows minutes."""
    for case in matrix["include"]:
        if case["skip"]:
            assert case["runner"] == "ubuntu-latest", case


def test_minimal_set_covers_all_operating_systems():
    """A pull request tests on Linux, Windows and macOS."""
    matrix = generate_matrix("refs/heads/pr-branch", "", "pull_request")
    running = {case["runner"] for case in matrix["include"] if not case["skip"]}
    assert running == RUNNERS


def test_full_run_covers_every_version_on_ubuntu():
    """Every supported Python version runs on Ubuntu when all jobs run."""
    matrix = generate_matrix("refs/heads/main", "", "push")
    versions = {
        case["python_version"]
        for case in matrix["include"]
        if not case["skip"] and case["runner"] == "ubuntu-latest"
    }
    assert {"3.10", "3.11", "3.12", "3.13", "3.14"} <= versions


@pytest.mark.parametrize(
    ("event_name", "git_ref", "expected_skip"),
    [
        ("push", "refs/heads/main", False),
        ("pull_request", "refs/pull/123/merge", True),
        ("schedule", "refs/heads/main", True),
        ("workflow_dispatch", "refs/heads/main", True),
        ("pull_request_review", "refs/heads/main", True),
        ("schedule", "refs/heads/8.x", True),
        ("push", "refs/heads/8.x", True),
        ("pull_request_review", "refs/heads/8.x", True),
    ],
)
def test_pypy_only_runs_on_push_to_main(event_name, git_ref, expected_skip):
    """Run the slow PyPy job after changes are merged or pushed to main."""
    matrix = generate_matrix(git_ref, "", event_name)
    pypy = next(
        case
        for case in matrix["include"]
        if case["test_name"] == "pypy3 (ubuntu-latest)"
    )
    assert pypy["skip"] is expected_skip
