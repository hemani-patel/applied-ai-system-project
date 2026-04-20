"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""
from .recommender import load_songs, recommend_songs

EDGE_CASES = {
    # High energy + sad mood — no song in the catalog satisfies both.
    # Watch whether the system compromises or lets one preference dominate.
    "Sad Workout": {
        "favorite_genre":      "metal",
        "favorite_mood":       "melancholic",
        "target_energy":       0.95,
        "likes_acoustic":      False,
        "target_valence":      0.25,
        "target_danceability": 0.50,
    },
    # Genre that does not exist in the catalog — every song scores 0 on genre.
    # The numerical features must carry the entire ranking on their own.
    "Unknown Genre": {
        "favorite_genre":      "k-pop",
        "favorite_mood":       "happy",
        "target_energy":       0.80,
        "likes_acoustic":      False,
        "target_valence":      0.85,
        "target_danceability": 0.88,
    },
    # likes_acoustic=True but target_energy=0.92 — contradictory preferences.
    # Every high-energy song has acousticness < 0.10; every acoustic song has energy < 0.45.
    # The system cannot satisfy both; watch which preference wins.
    "Acoustic Headbanger": {
        "favorite_genre":      "rock",
        "favorite_mood":       "intense",
        "target_energy":       0.92,
        "likes_acoustic":      True,
        "target_valence":      0.50,
        "target_danceability": 0.65,
    },
    # Genre match (edm) but every other preference is the opposite of Drop Zone.
    # Tests whether the +2.0 genre bonus incorrectly forces a bad song to #1.
    "Genre Trap": {
        "favorite_genre":      "edm",
        "favorite_mood":       "peaceful",
        "target_energy":       0.10,
        "likes_acoustic":      True,
        "target_valence":      0.70,
        "target_danceability": 0.30,
    },
}

PROFILES = {
    "High-Energy Pop": {
        "favorite_genre":    "pop",
        "favorite_mood":     "happy",
        "target_energy":     0.85,   # loud, upbeat
        "likes_acoustic":    False,  # prefers produced sound
        "target_valence":    0.82,   # very positive
        "target_danceability": 0.80,
    },
    "Chill Lofi": {
        "favorite_genre":    "lofi",
        "favorite_mood":     "focused",
        "target_energy":     0.38,   # calm, low-key
        "likes_acoustic":    True,   # warm, organic texture
        "target_valence":    0.58,   # neutral — not too happy, not sad
        "target_danceability": 0.60,
    },
    "Deep Intense Rock": {
        "favorite_genre":    "rock",
        "favorite_mood":     "intense",
        "target_energy":     0.92,   # raw, driving energy
        "likes_acoustic":    False,  # electric, amplified
        "target_valence":    0.45,   # darker, serious tone
        "target_danceability": 0.65,
    },
    "Late-Night Soul": {
        "favorite_genre":    "soul",
        "favorite_mood":     "romantic",
        "target_energy":     0.52,   # warm, mid-tempo
        "likes_acoustic":    True,   # rich, natural sound
        "target_valence":    0.72,   # smooth and emotional
        "target_danceability": 0.68,
    },
}

def run_profile(name, user_prefs, songs):
    """Run the recommender for one profile and print the results."""
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 60)
    print(f"  Profile: {name}".center(60))
    print("=" * 60)

    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n  #{i}  {song['title']}  ({song['artist']})")
        print(f"       Genre: {song['genre']}  |  Score: {score:.2f} / 4.50")
        print(f"       Why: {explanation}")

    print("\n" + "-" * 60)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    # Standard profiles
    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)

    # Adversarial / edge-case profiles
    print("\n\n" + "#" * 60)
    print("  EDGE CASE PROFILES".center(60))
    print("#" * 60)
    for name, prefs in EDGE_CASES.items():
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()
