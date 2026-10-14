import numpy as np
from src.utils import PCA_N_COMPONENTS


def find_similar_players(
    player_name,
    player_scores,
    median_pairwise_distance,
    n_neighbors=5,
    position_group=None,
):
    """
    Find the nearest players in PCA space using Euclidean distance.
    """
    pc_columns = [
        f"PC{i}" for i in range(1, PCA_N_COMPONENTS + 1)
    ]

    matches = player_scores.loc[player_scores["player"].eq(player_name)]

    if matches.empty:
        raise ValueError(f"Player not found: {player_name}")

    target_scores = matches[pc_columns].iloc[0].to_numpy()

    candidates = player_scores.loc[
        player_scores["player"].ne(player_name)
    ].copy()

    # Filter candidates by specified position group if necessary
    if position_group is not None:
        candidates = candidates.loc[
            candidates["position_group"].eq(position_group)
        ]

    candidate_scores = candidates[pc_columns].to_numpy()

    # Calculate Euclidean distances between target player and all candidates
    candidates["distance"] = np.linalg.norm(
        candidate_scores - target_scores,
        axis=1,
    )

    # Calculate similarity score relative to median distance
    candidates["similarity_score"] = (
        100 * 2 ** (
            -candidates["distance"] / median_pairwise_distance
        )
    )

    return (
        candidates
        .nsmallest(n_neighbors, "distance")
        [[
            "player",
            "teams",
            "primary_position",
            "position_group",
            "distance",
            "similarity_score"
        ]]
    )


