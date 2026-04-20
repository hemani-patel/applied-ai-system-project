# Music Recommender — Data Flow

```mermaid
flowchart TD
    A([User Preferences\ngenre · mood · target_energy · likes_acoustic]) --> B

    B[load_songs\nRead songs.csv → list of 20 song dicts] --> C

    C{For each song\nin catalog} --> D

    D[score_song\nCompute points] --> E
    E[Genre match?\n+2.0 or +0.0] --> F
    F[Mood match?\n+1.0 or +0.0] --> G
    G[Energy proximity\n+0.0 to +1.0] --> H
    H[Acousticness proximity\n+0.0 to +0.5] --> I

    I[Append\nsong · score · explanation\nto results list] --> J

    J{More songs?} -->|Yes| C
    J -->|No| K

    K[Sort results by score descending] --> L
    L[Slice top K] --> M

    M([Output\nRanked recommendations\nwith scores and explanations])

    style A fill:#4a90d9,color:#fff
    style M fill:#27ae60,color:#fff
    style D fill:#f5a623,color:#fff
    style K fill:#8e44ad,color:#fff
    style L fill:#8e44ad,color:#fff
```

## Stage legend

| Color | Stage | Code location |
|---|---|---|
| Blue | User input | `main.py` — `user_prefs` dict |
| Orange | Score one song | `recommender.py` — `score_song()` |
| Purple | Sort and slice | `recommender.py` — `recommend_songs()` |
| Green | Final output | `main.py` — `main()` print loop |
