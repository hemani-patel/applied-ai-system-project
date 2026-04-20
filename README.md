# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Real world systems like spoitify use a combo of collaboritive filtering which reccomeneds songs based on what similar users have listened to. The other way is content based filtering which recommends songs based on properties of the actual music. Platforms like spotify use both, like listening history, skips, and acoustic features together. My version however, will have to focus on content based filtering because we dont have user history data.  

features Song:
- id
- title
- artist
- genre
- mood
- energy
- danceability
- acousticness 
-valence
- tempo_BPM
- 

features userprofile:
- fav_genre
- fav_mood
- target_enerfy
- likes_acoustic

This recommender uses **content-based filtering** — it matches song attributes directly against a user's stated preferences. Real-world platforms like Spotify combine this with collaborative filtering (recommendations based on what similar users listened to), but this simulation focuses on content-based only since there is no user history data.

### Song Features

| Feature | Type | Role in scoring |
|---|---|---|
| `genre` | categorical | +2.0 if exact match |
| `mood` | categorical | +1.0 if exact match |
| `energy` | float 0–1 | proximity to `target_energy` → up to +1.0 |
| `acousticness` | float 0–1 | proximity to acoustic preference → up to +0.5 |
| `valence` | float 0–1 | musical positiveness (secondary signal) |
| `danceability` | float 0–1 | rhythm intensity (secondary signal) |
| `tempo_bpm` | float | speed in beats per minute (secondary signal) |

### User Profile

| Field | Type | Description |
|---|---|---|
| `genre` | string | preferred genre |
| `mood` | string | preferred mood |
| `target_energy` | float 0–1 | ideal energy level |
| `likes_acoustic` | bool | maps to acoustic target of 0.8 (True) or 0.2 (False) |

### Scoring Rule (per song)

```
score = genre match (+2.0 or 0)
      + mood match  (+1.0 or 0)
      + 1.0 × (1 − |song_energy − target_energy|)
      + 0.5 × (1 − |song_acousticness − acoustic_target|)

max possible score: 4.5
```

### Data Flow

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

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

## Recommendation Output

![Terminal output showing top song recommendations](images/output.png)

