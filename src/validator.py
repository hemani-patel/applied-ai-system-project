"""Input validation for user preference dicts passed to the recommender."""

import logging

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = (
    "genre",
    "mood",
    "target_energy",
    "likes_acoustic",
    "target_valence",
    "target_danceability",
)
_NUMERIC_KEYS = ("target_energy", "target_valence", "target_danceability")


def validate_user_prefs(user_prefs: dict) -> None:
    """Validate a user_prefs dict; raise ValueError with a helpful message on any issue."""

    # 1. All required keys must be present
    for key in _REQUIRED_KEYS:
        if key not in user_prefs:
            raise ValueError(
                f"Missing required key: '{key}'. "
                f"Expected keys: {list(_REQUIRED_KEYS)}"
            )

    # 2. String fields
    for str_key in ("genre", "mood"):
        val = user_prefs[str_key]
        if not isinstance(val, str):
            raise ValueError(
                f"'{str_key}' must be a string, got {type(val).__name__!r} ({val!r})"
            )

    # 3. Boolean field  (check before numeric — bool is a subclass of int in Python)
    val = user_prefs["likes_acoustic"]
    if not isinstance(val, bool):
        raise ValueError(
            f"'likes_acoustic' must be True or False, got {type(val).__name__!r} ({val!r})"
        )

    # 4. Numeric fields must be int/float and in [0.0, 1.0]
    for key in _NUMERIC_KEYS:
        val = user_prefs[key]
        # Explicitly reject booleans even though bool subclasses int
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise ValueError(
                f"'{key}' must be a number (int or float), got {type(val).__name__!r} ({val!r})"
            )
        if not (0.0 <= val <= 1.0):
            raise ValueError(
                f"'{key}' must be between 0.0 and 1.0 inclusive, got {val}"
            )

    logger.debug("validate_user_prefs passed for genre=%r mood=%r",
                 user_prefs["genre"], user_prefs["mood"])
