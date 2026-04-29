"""
CLI entry point for the Music Recommender.

Two modes, selected by command-line argument:

  python -m src.main           — recommendation mode
      Loads the song catalog, runs predefined standard and edge-case
      profiles through the full pipeline, and prints ranked results
      with scores, confidence labels, and explanations.

  python -m src.main --test    — evaluator mode
      Runs the reliability evaluator against the live pipeline and
      prints a structured pass/fail summary for each test profile.
      Exits with code 1 if any test fails (useful for CI).
"""
import logging
import os
import sys

from .recommender import load_songs, recommend_songs, check_catalog_coverage
from .validator import validate_user_prefs
from .evaluator import run_reliability_tests

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    """Configure console (INFO) and file (DEBUG) handlers for all app loggers."""
    os.makedirs("logs", exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Console: INFO and above, compact single-line format
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    # File: DEBUG and above, timestamped format — appends across runs
    file_handler = logging.FileHandler("logs/recommendation.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    root.addHandler(console)
    root.addHandler(file_handler)


def log_recommendation_run(name: str, user_prefs: dict, recommendations: list) -> None:
    """Log a completed recommendation run: profile inputs, ranked results, and reasons."""
    logger.info(
        "Profile '%s' | genre=%s  mood=%s  energy=%.2f  acoustic=%s",
        name,
        user_prefs["genre"],
        user_prefs["mood"],
        user_prefs["target_energy"],
        user_prefs["likes_acoustic"],
    )
    for rank, (song, score, explanation, confidence) in enumerate(recommendations, 1):
        logger.info(
            "  #%d  %-28s  score=%.2f  confidence=%s",
            rank, song["title"], score, confidence,
        )
        logger.debug("       reasons: %s", explanation)

EDGE_CASES = {
    # High energy + sad mood — no song in the catalog satisfies both.
    # Watch whether the system compromises or lets one preference dominate.
    "Sad Workout": {
        "genre":      "metal",
        "mood":       "melancholic",
        "target_energy":       0.95,
        "likes_acoustic":      False,
        "target_valence":      0.25,
        "target_danceability": 0.50,
    },
    # Genre that does not exist in the catalog — every song scores 0 on genre.
    # The numerical features must carry the entire ranking on their own.
    "Unknown Genre": {
        "genre":      "k-pop",
        "mood":       "happy",
        "target_energy":       0.80,
        "likes_acoustic":      False,
        "target_valence":      0.85,
        "target_danceability": 0.88,
    },
    # likes_acoustic=True but target_energy=0.92 — contradictory preferences.
    # Every high-energy song has acousticness < 0.10; every acoustic song has energy < 0.45.
    # The system cannot satisfy both; watch which preference wins.
    "Acoustic Headbanger": {
        "genre":      "rock",
        "mood":       "intense",
        "target_energy":       0.92,
        "likes_acoustic":      True,
        "target_valence":      0.50,
        "target_danceability": 0.65,
    },
    # Genre match (edm) but every other preference is the opposite of Drop Zone.
    # Tests whether the +2.0 genre bonus incorrectly forces a bad song to #1.
    "Genre Trap": {
        "genre":      "edm",
        "mood":       "peaceful",
        "target_energy":       0.10,
        "likes_acoustic":      True,
        "target_valence":      0.70,
        "target_danceability": 0.30,
    },
}

PROFILES = {
    "High-Energy Pop": {
        "genre":    "pop",
        "mood":     "happy",
        "target_energy":     0.85,   # loud, upbeat
        "likes_acoustic":    False,  # prefers produced sound
        "target_valence":    0.82,   # very positive
        "target_danceability": 0.80,
    },
    "Chill Lofi": {
        "genre":    "lofi",
        "mood":     "focused",
        "target_energy":     0.38,   # calm, low-key
        "likes_acoustic":    True,   # warm, organic texture
        "target_valence":    0.58,   # neutral — not too happy, not sad
        "target_danceability": 0.60,
    },
    "Deep Intense Rock": {
        "genre":    "rock",
        "mood":     "intense",
        "target_energy":     0.92,   # raw, driving energy
        "likes_acoustic":    False,  # electric, amplified
        "target_valence":    0.45,   # darker, serious tone
        "target_danceability": 0.65,
    },
    "Late-Night Soul": {
        "genre":    "soul",
        "mood":     "romantic",
        "target_energy":     0.52,   # warm, mid-tempo
        "likes_acoustic":    True,   # rich, natural sound
        "target_valence":    0.72,   # smooth and emotional
        "target_danceability": 0.68,
    },
}

def run_profile(name, user_prefs, songs):
    """Run the recommender for one profile and print the results."""
    try:
        validate_user_prefs(user_prefs)
    except ValueError as e:
        logger.warning("Skipping profile '%s' — validation failed: %s", name, e)
        print(f"\n[Skipping '{name}'] Invalid profile — {e}")
        return

    coverage = check_catalog_coverage(user_prefs, songs)
    for note in coverage["notes"]:
        logger.warning("Profile '%s' — %s", name, note)

    recommendations = recommend_songs(user_prefs, songs, k=5)
    log_recommendation_run(name, user_prefs, recommendations)

    print("\n" + "=" * 60)
    print(f"  Profile: {name}".center(60))
    print("=" * 60)

    # Surface fallback notes so the user knows no exact categorical match existed
    for note in coverage["notes"]:
        print(f"\n  [Note] {note}")

    for i, (song, score, explanation, confidence) in enumerate(recommendations, 1):
        print(f"\n  #{i}  {song['title']}  ({song['artist']})")
        print(f"       Genre: {song['genre']}  |  Score: {score:.2f} / 4.50  |  Confidence: {confidence}")
        print(f"       Why: {explanation}")

    print("\n" + "-" * 60)


def main() -> None:
    """Run the recommender in recommendation mode or evaluator mode.

    Pass --test to run the reliability evaluator instead of normal recommendations.
    The evaluator exits with code 1 if any test fails.
    """
    _setup_logging()
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    if "--test" in sys.argv:
        all_passed = run_reliability_tests(songs)
        sys.exit(0 if all_passed else 1)

    logger.info("=== Music Recommender started ===")

    # Standard profiles
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)

    # Adversarial / edge-case profiles
    print("\n\n" + "#" * 60)
    print("  EDGE CASE PROFILES".center(60))
    print("#" * 60)
    for name, prefs in EDGE_CASES.items():
        run_profile(name, prefs, songs)

    logger.info("=== Music Recommender finished ===")


if __name__ == "__main__":
    main()
