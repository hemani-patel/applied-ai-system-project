from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV of songs and return a list of dicts with numeric fields cast to float/int."""
    import csv

    songs = []

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields from strings to numbers
            song = {
                "id":            int(row["id"]),
                "title":         row["title"],
                "artist":        row["artist"],
                "genre":         row["genre"],
                "mood":          row["mood"],
                "energy":        float(row["energy"]),
                "tempo_bpm":     float(row["tempo_bpm"]),
                "valence":       float(row["valence"]),
                "danceability":  float(row["danceability"]),
                "acousticness":  float(row["acousticness"]),
            }
            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (total_points, list of reasons)."""
    total_score = 0.0
    reasons = []
    
    # Genre exact match: +2.0 points
    if song["genre"].lower() == user_prefs["favorite_genre"].lower():
        total_score += 2.0
        reasons.append("genre match (+2.0)")
    
    # Mood exact match: +1.0 point  [COMMENTED OUT FOR SENSITIVITY TEST]
    # if song["mood"].lower() == user_prefs["favorite_mood"].lower():
    #     total_score += 1.0
    #     reasons.append("mood match (+1.0)")
    
    # Energy similarity: 0.0 to 1.5 points  [raised from 1.0 — absorbs half of removed mood weight]
    energy_points = 1.5 * (1 - abs(song["energy"] - user_prefs["target_energy"]))
    total_score += energy_points
    reasons.append(f"energy close to target (+{energy_points:.2f})")

    # Acousticness similarity: 0.0 to 1.0 points  [raised from 0.5 — absorbs other half of removed mood weight]
    acoustic_target = 0.80 if user_prefs["likes_acoustic"] else 0.20
    acoustic_points = 1.0 * (1 - abs(song["acousticness"] - acoustic_target))
    total_score += acoustic_points
    reasons.append(f"acousticness matches preference (+{acoustic_points:.2f})")
    
    return total_score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort by score descending, and return the top k as (song, score, explanation) tuples."""
    # Score every song and collect results
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    # Sort by score (highest first) and return the top k
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
