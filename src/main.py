"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""
from .recommender import load_songs, recommend_songs

def main() -> None:
    songs = load_songs("data/songs.csv") 
    print("Loaded songs:", len(songs))
    
    # Late-night study session listener
    # user_prefs = {
    #     "genre":          "lofi",    # preferred genre
    #     "mood":           "focused", # preferred mood
    #     "target_energy":  0.40,      # low energy — calm, not distracting
    #     "likes_acoustic": True,      # prefers acoustic texture
    #     "target_valence": 0.58,      # neutral-to-positive, not too emotional
    #     "target_danceability": 0.60, # moderate — rhythmic but not club-ready
    # }
    #stronger profile suggested by claude
    user_prefs = {
    "favorite_genre":             "pop",    # only 1 jazz song — forces numerical features to matter
    "favorite_mood":              "happy",
    "target_energy":     0.75,      # mid-range — forces ranking across many songs
    "likes_acoustic":    False,
    "target_valence":    0.80,
    "target_danceability": 0.75,
}


    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*60)
    print("TOP 5 RECOMMENDATIONS".center(60))
    print("="*60 + "\n")
    
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"{i}. {song['title']}")
        print(f"   Score: {score:.2f}/4.50")
        print(f"   Why: {explanation}")
        print()
    
    print("="*60)


if __name__ == "__main__":
    main()
