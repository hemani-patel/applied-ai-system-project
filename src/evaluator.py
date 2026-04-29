"""Reliability evaluator: runs predefined profiles through the full pipeline and reports pass/fail."""

import logging
from typing import List, Tuple

from .recommender import recommend_songs, check_catalog_coverage
from .validator import validate_user_prefs

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Standard test profiles — all fields valid, genre and mood present in catalog
# ---------------------------------------------------------------------------

STANDARD_PROFILES = {
    "Pop / Happy": {
        "description": "Genre+mood both in catalog — expect genre match, mood match, and High confidence.",
        "prefs": {
            "genre": "pop", "mood": "happy",
            "target_energy": 0.85, "likes_acoustic": False,
            "target_valence": 0.82, "target_danceability": 0.80,
        },
    },
    "Chill Lofi": {
        # Catalog has "Focus Flow" (lofi + focused), so both genre and mood match are testable.
        "description": "Acoustic, low-energy genre in catalog — expect genre match, mood match, and Medium+ confidence.",
        "prefs": {
            "genre": "lofi", "mood": "focused",
            "target_energy": 0.38, "likes_acoustic": True,
            "target_valence": 0.58, "target_danceability": 0.60,
        },
    },
    "High-Energy Rock": {
        # Catalog has "Storm Runner" (rock + intense), so both genre and mood match are testable.
        "description": "High-energy, electric genre in catalog — expect genre match, mood match, and Medium+ confidence.",
        "prefs": {
            "genre": "rock", "mood": "intense",
            "target_energy": 0.92, "likes_acoustic": False,
            "target_valence": 0.45, "target_danceability": 0.65,
        },
    },
    "Relaxed Jazz": {
        # Catalog has exactly one jazz song: "Coffee Shop Stories" (jazz + relaxed).
        "description": "Acoustic, low-energy genre with relaxed mood — expect genre match, mood match, and Medium+ confidence.",
        "prefs": {
            "genre": "jazz", "mood": "relaxed",
            "target_energy": 0.35, "likes_acoustic": True,
            "target_valence": 0.60, "target_danceability": 0.45,
        },
    },
}

# ---------------------------------------------------------------------------
# Edge-case profiles — structurally valid, but genre or mood absent from catalog
# ---------------------------------------------------------------------------

EDGE_CASE_PROFILES = {
    "Unknown Genre": {
        "description": "Genre 'k-pop' not in catalog — system falls back to numerical scoring and emits a warning note.",
        "prefs": {
            "genre": "k-pop", "mood": "happy",
            "target_energy": 0.80, "likes_acoustic": False,
            "target_valence": 0.85, "target_danceability": 0.88,
        },
    },
    "Unknown Mood": {
        "description": "Mood 'bored' not in catalog — system falls back to genre+numerical scoring and emits a warning note.",
        "prefs": {
            "genre": "pop", "mood": "bored",
            "target_energy": 0.60, "likes_acoustic": False,
            "target_valence": 0.50, "target_danceability": 0.55,
        },
    },
}

# ---------------------------------------------------------------------------
# Invalid profiles — must be rejected by validate_user_prefs before any scoring
# ---------------------------------------------------------------------------

INVALID_PROFILES = {
    "Invalid Energy": {
        "description": "target_energy=1.8 is outside [0.0, 1.0] — validator must raise ValueError.",
        "prefs": {
            "genre": "pop", "mood": "happy",
            "target_energy": 1.8,
            "likes_acoustic": False,
            "target_valence": 0.80, "target_danceability": 0.70,
        },
    },
    "Missing Genre Key": {
        "description": "'genre' key absent entirely — validator must raise ValueError for missing required key.",
        "prefs": {
            "mood": "happy",
            "target_energy": 0.80, "likes_acoustic": False,
            "target_valence": 0.80, "target_danceability": 0.70,
        },
    },
}


# ---------------------------------------------------------------------------
# Check helpers — each returns (passed: bool, detail: str)
# ---------------------------------------------------------------------------

def _has_k_results(recs: list, k: int = 5) -> Tuple[bool, str]:
    """Check that exactly k recommendations were returned."""
    if len(recs) == k:
        return True, f"returned {k} recommendations"
    return False, f"expected {k} results, got {len(recs)}"


def _has_genre_match(recs: list, genre: str) -> Tuple[bool, str]:
    """Check that at least one top-k result matches the requested genre."""
    if any(r[0]["genre"].lower() == genre.lower() for r in recs):
        return True, f"genre match found for '{genre}'"
    return False, f"no result matched genre '{genre}'"


def _has_no_genre_match(recs: list, genre: str) -> Tuple[bool, str]:
    """Check that no top-k result matches the genre (used to confirm fallback mode)."""
    if not any(r[0]["genre"].lower() == genre.lower() for r in recs):
        return True, f"no '{genre}' song in results (genre not in catalog — expected)"
    return False, f"unexpectedly found a '{genre}' result when genre is not in catalog"


def _has_mood_match(recs: list, mood: str) -> Tuple[bool, str]:
    """Check that at least one top-k result matches the requested mood."""
    if any(r[0]["mood"].lower() == mood.lower() for r in recs):
        return True, f"mood match found for '{mood}'"
    return False, f"no result matched mood '{mood}'"


def _has_no_mood_match(recs: list, mood: str) -> Tuple[bool, str]:
    """Check that no top-k result matches the mood (used to confirm fallback mode)."""
    if not any(r[0]["mood"].lower() == mood.lower() for r in recs):
        return True, f"no '{mood}' song in results (mood not in catalog — expected)"
    return False, f"unexpectedly found a '{mood}' result when mood is not in catalog"


def _has_medium_or_high(recs: list) -> Tuple[bool, str]:
    """Check that at least one result has Medium or High confidence."""
    if not recs:
        return False, "no results to evaluate confidence"
    if any(r[3] in ("Medium", "High") for r in recs):
        top = recs[0]
        return True, f"top result: score={top[1]:.2f}, confidence={top[3]}"
    return False, f"all results are Low confidence (top score={recs[0][1]:.2f})"


def _has_fallback_notes(coverage: dict) -> Tuple[bool, str]:
    """Check that catalog-coverage notes exist, meaning fallback mode was triggered."""
    if coverage["notes"]:
        return True, f"fallback note: {coverage['notes'][0]}"
    return False, "expected a fallback warning note but none was generated"


def _fails_validation(prefs: dict, expected_field: str = "") -> Tuple[bool, str]:
    """Check that validate_user_prefs raises ValueError; if expected_field is given, verify it appears in the message."""
    try:
        validate_user_prefs(prefs)
        return False, "expected ValueError but profile passed validation"
    except ValueError as e:
        msg = str(e)
        if expected_field and expected_field not in msg:
            return False, f"raised ValueError but message did not mention '{expected_field}': {msg}"
        if expected_field:
            return True, f"raised ValueError mentioning '{expected_field}'"
        return True, f"raised ValueError: {msg}"


# ---------------------------------------------------------------------------
# Core runner — executes every check and collects per-check results
# ---------------------------------------------------------------------------

def _run_all_checks(checks: list) -> Tuple[bool, List[str]]:
    """Run every check regardless of earlier failures; return (all_passed, list of detail lines).

    Uses ✓/✗ markers so sub-check lines are visually distinct from the top-level [PASS]/[FAIL] label.
    """
    lines = []
    all_passed = True
    for fn, args in checks:
        passed, detail = fn(*args)
        lines.append(f"{'✓' if passed else '✗'} {detail}")
        if not passed:
            all_passed = False
    return all_passed, lines


# ---------------------------------------------------------------------------
# Individual test functions — each returns (passed: bool, check_lines: list[str])
# ---------------------------------------------------------------------------

def _test_pop_happy(songs: list) -> Tuple[bool, List[str]]:
    """Pop/happy: 5 results, genre match, mood match, Medium+ confidence."""
    prefs = STANDARD_PROFILES["Pop / Happy"]["prefs"]
    try:
        validate_user_prefs(prefs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,       (recs,)),
        (_has_genre_match,     (recs, "pop")),
        (_has_mood_match,      (recs, "happy")),
        (_has_medium_or_high,  (recs,)),
    ])


def _test_chill_lofi(songs: list) -> Tuple[bool, List[str]]:
    """Chill lofi: 5 results, genre match, mood match, Medium+ confidence.
    Catalog has 'Focus Flow' (lofi + focused), so mood match is reliable.
    """
    prefs = STANDARD_PROFILES["Chill Lofi"]["prefs"]
    try:
        validate_user_prefs(prefs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,       (recs,)),
        (_has_genre_match,     (recs, "lofi")),
        (_has_mood_match,      (recs, "focused")),
        (_has_medium_or_high,  (recs,)),
    ])


def _test_rock_intense(songs: list) -> Tuple[bool, List[str]]:
    """High-energy rock: 5 results, genre match, mood match, Medium+ confidence.
    Catalog has 'Storm Runner' (rock + intense), so mood match is reliable.
    """
    prefs = STANDARD_PROFILES["High-Energy Rock"]["prefs"]
    try:
        validate_user_prefs(prefs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,       (recs,)),
        (_has_genre_match,     (recs, "rock")),
        (_has_mood_match,      (recs, "intense")),
        (_has_medium_or_high,  (recs,)),
    ])


def _test_jazz_relaxed(songs: list) -> Tuple[bool, List[str]]:
    """Relaxed jazz: 5 results, genre match, mood match, Medium+ confidence.
    Catalog has exactly one jazz song: 'Coffee Shop Stories' (jazz + relaxed).
    """
    prefs = STANDARD_PROFILES["Relaxed Jazz"]["prefs"]
    try:
        validate_user_prefs(prefs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,       (recs,)),
        (_has_genre_match,     (recs, "jazz")),
        (_has_mood_match,      (recs, "relaxed")),
        (_has_medium_or_high,  (recs,)),
    ])


def _test_unknown_genre(songs: list) -> Tuple[bool, List[str]]:
    """Unknown genre (k-pop): 5 fallback results, warning note emitted, no k-pop song in results."""
    prefs = EDGE_CASE_PROFILES["Unknown Genre"]["prefs"]
    try:
        validate_user_prefs(prefs)
        coverage = check_catalog_coverage(prefs, songs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,          (recs,)),
        (_has_fallback_notes,     (coverage,)),
        (_has_no_genre_match,     (recs, "k-pop")),
    ])


def _test_unknown_mood(songs: list) -> Tuple[bool, List[str]]:
    """Unknown mood (bored): 5 fallback results, warning note emitted, no 'bored' song in results."""
    prefs = EDGE_CASE_PROFILES["Unknown Mood"]["prefs"]
    try:
        validate_user_prefs(prefs)
        coverage = check_catalog_coverage(prefs, songs)
        recs = recommend_songs(prefs, songs, k=5)
    except Exception as e:
        return False, [f"✗ unexpected error: {e}"]

    return _run_all_checks([
        (_has_k_results,         (recs,)),
        (_has_fallback_notes,    (coverage,)),
        (_has_no_mood_match,     (recs, "bored")),
    ])


def _test_invalid_energy(songs: list) -> Tuple[bool, List[str]]:
    """target_energy=1.8: validator must raise ValueError and the message must mention 'target_energy'."""
    return _run_all_checks([
        (_fails_validation, (INVALID_PROFILES["Invalid Energy"]["prefs"], "target_energy")),
    ])


def _test_missing_key(songs: list) -> Tuple[bool, List[str]]:
    """Missing 'genre' key: validator must raise ValueError and the message must mention 'genre'."""
    return _run_all_checks([
        (_fails_validation, (INVALID_PROFILES["Missing Genre Key"]["prefs"], "genre")),
    ])


# ---------------------------------------------------------------------------
# Master test registry and evaluator entry point
# ---------------------------------------------------------------------------

_TESTS = [
    ("Pop / Happy — genre, mood, confidence",              _test_pop_happy),
    ("Chill Lofi — genre, mood, confidence",               _test_chill_lofi),
    ("High-Energy Rock — genre, mood, confidence",         _test_rock_intense),
    ("Relaxed Jazz — genre, mood, confidence",             _test_jazz_relaxed),
    ("Unknown Genre — fallback, note, no k-pop result",    _test_unknown_genre),
    ("Unknown Mood — fallback, note, no bored result",     _test_unknown_mood),
    ("Invalid Numeric Input — ValueError on target_energy", _test_invalid_energy),
    ("Missing Required Key — ValueError on genre",         _test_missing_key),
]


def run_reliability_tests(songs: list) -> bool:
    """Run all reliability tests against the live pipeline and print a pass/fail summary."""
    logger.info("=== Reliability Evaluator started ===")

    total = len(_TESTS)

    print("\n" + "=" * 70)
    print("  RELIABILITY EVALUATOR".center(70))
    print("=" * 70)
    print(f"\n  Running {total} reliability tests against the live pipeline...\n")

    passed_count = 0

    for name, test_fn in _TESTS:
        try:
            passed, check_lines = test_fn(songs)
        except Exception as e:
            passed, check_lines = False, [f"✗ unhandled exception: {e}"]

        label = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1

        print(f"  [{label}]  {name}")
        for line in check_lines:
            print(f"           {line}")
        print()
        logger.info("  [%s] %s — %s", label, name, "; ".join(check_lines))

    failed_count = total - passed_count
    print("-" * 70)
    print("  Summary")
    print(f"  {passed_count} out of {total} tests passed.")
    if failed_count > 0:
        print(f"  {failed_count} {'test' if failed_count == 1 else 'tests'} failed.")
    print("=" * 70 + "\n")
    logger.info(
        "=== Reliability Evaluator finished: %d/%d tests passed ===",
        passed_count, total,
    )

    return passed_count == total
