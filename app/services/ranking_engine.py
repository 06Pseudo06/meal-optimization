from app.core.scoring_config import SCORING_WEIGHTS


def compute_score(features):

    score = 0

    for feature_name, weight in SCORING_WEIGHTS.items():
        score += weight * features.get(feature_name, 0)

    return score
