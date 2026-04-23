import math

def calculate_opportunity_score(
        volume: int,
        difficulty: int,
        domain_visible: bool,
        visibility_position: int | None,
        intent_type: str
) -> float:
    """
    Calculates the opportunity score (0 to 1) using the multi factor weighted formula.
    """
    # normalize volume (Log scale, max baseline 10000)
    # log10(1 + volume) / log10(10001)
    norm_vol = min(math.log10(1 + max(volume, 0)) / math.log10(10001), 1)

    # normalize difficulty (inverted: lower difficulty = higher opportunity)
    norm_diff = difficulty / 100

    # visibility gap multiplier
    if not domain_visible or visibility_position is None:
        vis_gap = 1
    elif 4 <= visibility_position <= 10:
        vis_gap = 0.5
    elif 1 <= visibility_position <= 3:
        vis_gap = 0.1
    else:
        vis_gap = 1  # fallback if position is > 10 but marked visible

    # commercial intent multiplier
    intent_map = {
        "transactional": 1,
        "comparison": 1,
        "evaluation": 0.7,
        "informational": 0.4,
        "navigational": 0.1
    }
    intent_score = intent_map.get(intent_type.lower(), 0.4)

    # Apply weighted formula
    score = (0.30 * norm_vol) + (0.25 * (1 - norm_diff)) + (0.30 * vis_gap) + (0.15 * intent_score)

    return round(max(0.0, min(score, 1)), 4)