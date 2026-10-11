from pathlib import Path
import pandas as pd
import numpy as np

from utils import season_ids, top_league_comp_ids


def build_player_season_features(competition_id, season_id):
    """
    Build player season features for a given competition and season given engineered player match feature table.
    """

    competitions_by_id = {value: key for key, value in top_league_comp_ids.items()}
    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        competition = competitions_by_id[competition_id]
    except KeyError as exc:
        raise ValueError(f"Unknown competition_id: {competition_id}") from exc

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    print(f"Compiling season-long features for competition: {competition}, season: {season}....")

    project_dir = Path(__file__).resolve().parent.parent
    processed_dir = project_dir / "data/processed" / competition / season
    features_path = processed_dir / "player_match_features.parquet"
    positions_path = processed_dir / "player_positions.parquet"

    player_positions = pd.read_parquet(positions_path)
    match_features = pd.read_parquet(features_path)

    season_totals = (
        match_features.groupby("player_id", as_index=False)
            .agg(
                # Descriptive fields
                player=("player", "first"),
                team_ids=("team_id", lambda x: list(x.dropna().unique())),
                teams=("team", lambda x: list(x.dropna().unique())),

                # Playing time
                matches_played=("match_id", "nunique"),
                starts=("started", "sum"),
                minutes_played=("minutes_played", "sum"),

                # Passing / creation
                passes_attempted=("passes_attempted", "sum"),
                passes_completed=("passes_completed", "sum"),
                progressive_passes=("progressive_passes", "sum"),
                shot_assists=("shot_assists", "sum"),
                assists=("assists", "sum"),
                xA=("xA", "sum"),

                # Dribbling / carrying
                dribbles_attempted=("dribbles_attempted", "sum"),
                dribbles_completed=("dribbles_completed", "sum"),
                carries=("carries", "sum"),
                progressive_carries=("progressive_carries", "sum"),

                # Shooting
                shots=("shots", "sum"),
                shots_on_target=("shots_on_target", "sum"),
                xG=("xG", "sum"),
                goals=("goals", "sum"),

                # Defending
                duels=("duels", "sum"),
                tackles_attempted=("tackles_attempted", "sum"),
                tackles_won=("tackles_won", "sum"),
                poss_won_final_third_tackles=(
                    "poss_won_final_third_tackles", "sum"
                ),
                clearances=("clearances", "sum"),
                blocks=("blocks", "sum"),
                interceptions=("interceptions", "sum"),
                interceptions_won=("interceptions_won", "sum"),
                poss_won_final_third_interceptions=(
                    "poss_won_final_third_interceptions", "sum"
                ),
                ball_recoveries_attempted=(
                    "ball_recoveries_attempted", "sum"
                ),
                ball_recoveries_won=(
                    "ball_recoveries_won", "sum"
                ),

                # Pressing / discipline
                pressures=("pressures", "sum"),
                fouls=("fouls", "sum"),
            )
        )

    # Add competition/season metadata
    season_totals.insert(0, "competition_id", competition_id)
    season_totals.insert(1, "competition", competition)
    season_totals.insert(2, "season_id", season_id)
    season_totals.insert(3, "season", season)

    # Combine poss won final third metrics
    season_totals["poss_won_final_third"] = (
        season_totals["poss_won_final_third_interceptions"]
        + season_totals["poss_won_final_third_tackles"]
    )
    season_totals = season_totals.drop(
        columns=[
            "poss_won_final_third_interceptions",
            "poss_won_final_third_tackles",
        ]
    )

    # Derived efficiency metrics
    season_totals["pass_completion_pct"] = (
        season_totals["passes_completed"]
        / season_totals["passes_attempted"]
    )
    season_totals["dribble_completion_pct"] = (
        season_totals["dribbles_completed"]
        / season_totals["dribbles_attempted"]
    )
    season_totals["shot_accuracy_pct"] = (
        season_totals["shots_on_target"]
        / season_totals["shots"]
    )
    season_totals["tackle_win_pct"] = (
        season_totals["tackles_won"]
        / season_totals["tackles_attempted"]
    )
    season_totals["goals_minus_xG"] = (
        season_totals["goals"] - season_totals["xG"]
    )
    season_totals["assists_minus_xA"] = (
        season_totals["assists"] - season_totals["xA"]
    )

    # Add player position information
    position_cols = player_positions[
        [
            "player_id",
            "primary_position",
            "position_group",
        ]
    ]
    season_totals = season_totals.merge(
        position_cols,
        on="player_id",
        how="left",
        validate="one_to_one",
    )

    # Save completed player-season feature table
    output_path = processed_dir / "player_season_features.parquet"
    season_totals.to_parquet(output_path, index=False)

    print(f"Saved {len(season_totals):,} player-season rows to {output_path}")

    
def build_player_match_features(competition_id, season_id):
    """
    Build player match features for a given competition and season.
    """

    competitions_by_id = {value: key for key, value in top_league_comp_ids.items()}
    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        competition = competitions_by_id[competition_id]
    except KeyError as exc:
        raise ValueError(f"Unknown competition_id: {competition_id}") from exc

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    print(f"Building match-level features for competition: {competition}, season: {season}....")

    project_dir = Path(__file__).resolve().parent.parent
    processed_dir = project_dir / "data/processed" / competition / season

    # Aggregate each event type to the player-match level
    pass_features = aggregate_pass_features(processed_dir)
    dribble_features = aggregate_dribble_features(processed_dir)
    carry_features = aggregate_carry_features(processed_dir)
    shot_features = aggregate_shot_features(processed_dir)
    duel_features = aggregate_duel_features(processed_dir)
    clearance_features = aggregate_clearance_features(processed_dir)
    block_features = aggregate_block_features(processed_dir)
    interception_features = aggregate_interception_features(processed_dir)
    ball_recovery_features = aggregate_ball_recovery_features(processed_dir)
    pressure_features = aggregate_pressure_features(processed_dir)
    foul_features = aggregate_foul_features(processed_dir)

    # Use player minutes as the base table to retain all match appearances
    minutes_path = processed_dir / "player_minutes.parquet"
    proc_minutes = pd.read_parquet(minutes_path)

    feature_tables = [
        pass_features,
        dribble_features,
        carry_features,
        shot_features,
        duel_features,
        clearance_features,
        block_features,
        interception_features,
        ball_recovery_features,
        pressure_features,
        foul_features,
    ]

    # Merge event features onto each player-match appearance
    player_match_features = proc_minutes.copy()

    for feature_table in feature_tables:
        player_match_features = player_match_features.merge(
            feature_table,
            how="left",
            on=["match_id", "player_id"],
        )

    # Replace missing event features with zero
    feature_columns = [
        column
        for feature_table in feature_tables
        for column in feature_table.columns
        if column not in {"match_id", "player_id"}
    ]

    player_match_features[feature_columns] = (
        player_match_features[feature_columns].fillna(0)
    )

    # Save completed player-match feature table
    output_path = processed_dir / "player_match_features.parquet"
    player_match_features.to_parquet(output_path, index=False)

    print(f"Saved {len(player_match_features):,} player-match rows to {output_path}")


def aggregate_pass_features(processed_dir):
    """
    Aggregates pass events to the player-match level.
    """
    print("Aggregating pass features...")

    passes_path = processed_dir / "passes.parquet"
    proc_passes = pd.read_parquet(passes_path)

    # load in shots xG figures for xA calculation
    shots_path = processed_dir / "shots.parquet"
    proc_shots = pd.read_parquet(shots_path)
    shot_xg = proc_shots[["match_id", "id", "shot_statsbomb_xg"]].rename(
        columns={
            "id": "shot_id",
            "shot_statsbomb_xg": "assisted_shot_xg"
        }
    )

    # merge in xA figures
    proc_passes = proc_passes.merge(
        shot_xg,
        how="left",
        left_on=["match_id", "pass_assisted_shot_id"],
        right_on=["match_id", "shot_id"]
    )
    proc_passes["xA"] = proc_passes["assisted_shot_xg"].fillna(0)

    # use helper to flag progressive passes
    proc_passes["progressive_pass"] = (
        proc_passes.apply(
            lambda row: is_progressive_action(
                row["x"],
                row["y"],
                row["end_x"],
                row["end_y"]
            ),
            axis=1
        )
        & proc_passes["completed"]
    )

    # make shot assist include shots that scored
    proc_passes["shot_assist"] = (
        proc_passes["pass_shot_assist"].fillna(False)
        | proc_passes["pass_goal_assist"].fillna(False)
    )

    pass_features = (
        proc_passes
        .groupby(["match_id", "player_id"])
        .agg(
            passes_attempted=("player_id", "size"),
            passes_completed=("completed", "sum"),
            progressive_passes=("progressive_pass", "sum"),
            shot_assists=("shot_assist", "sum"),
            assists=("pass_goal_assist", "sum"),
            xA=("xA", "sum")
        )
        .reset_index()
    )

    return pass_features


def aggregate_dribble_features(processed_dir):
    """
    Aggregates dribble events to the player-match level.
    """
    print("Aggregating dribble features...")

    dribbles_path = processed_dir / "dribbles.parquet"
    proc_dribbles = pd.read_parquet(dribbles_path)

    dribble_features = (
        proc_dribbles
        .groupby(["match_id", "player_id"])
        .agg(
            dribbles_attempted=("player_id", "size"),
            dribbles_completed=("dribble_completed", "sum"),
        )
        .reset_index()
    )

    return dribble_features


def aggregate_carry_features(processed_dir):
    """
    Aggregates carry events to the player-match level.
    """
    print("Aggregating carry features...")

    carries_path = processed_dir / "carries.parquet"
    proc_carries = pd.read_parquet(carries_path)
    
    proc_carries["progressive_carry"] = proc_carries.apply(
        lambda row: is_progressive_action(
            row["x"],
            row["y"],
            row["end_x"],
            row["end_y"]
        ),
        axis=1
    )

    carry_features = (
        proc_carries
        .groupby(["match_id", "player_id"])
        .agg(
            carries=("player_id", "size"),
            progressive_carries=("progressive_carry", "sum"),
        )
        .reset_index()
    )

    return carry_features


def aggregate_shot_features(processed_dir):
    """
    Aggregates shot events to the player-match level.
    """
    print("Aggregating shot features...")

    shots_path = processed_dir / "shots.parquet"
    proc_shots = pd.read_parquet(shots_path)

    shot_features = (
        proc_shots
        .groupby(["match_id", "player_id"])
        .agg(
            shots=("player_id", "size"),
            shots_on_target=("on_target", "sum"),
            xG=("shot_statsbomb_xg", "sum"),
            goals=("scored", "sum")
        )
        .reset_index()
    )

    return shot_features


def aggregate_duel_features(processed_dir):
    """
    Aggregates duel events to the player-match level.
    """
    print("Aggregating duel features...")

    duels_path = processed_dir / "duels.parquet"
    proc_duels = pd.read_parquet(duels_path)

    # Successful tackle occurring in the attacking third
    proc_duels["poss_won_final_third"] = (
        proc_duels["tackle_won"]
        & (proc_duels["x"] >= 80)
    )
    
    duel_features = (
        proc_duels
        .groupby(["match_id", "player_id"])
        .agg(
            duels=("player_id", "size"),
            tackles_attempted=("tackle_attempted", "sum"),
            tackles_won=("tackle_won", "sum"),
            poss_won_final_third_tackles=(
                "poss_won_final_third",
                "sum",
            ),
        )
        .reset_index()
    )

    return duel_features


def aggregate_clearance_features(processed_dir):
    """
    Aggregates clearance events to the player-match level.
    """
    print("Aggregating clearance features...")

    clearances_path = processed_dir / "clearances.parquet"
    proc_clearances = pd.read_parquet(clearances_path)

    clearance_features = (
        proc_clearances
        .groupby(["match_id", "player_id"])
        .size()
        .reset_index(name="clearances")
    )

    return clearance_features


def aggregate_block_features(processed_dir):
    """
    Aggregates block events to the player-match level.
    """
    print("Aggregating block features...")

    blocks_path = processed_dir / "blocks.parquet"
    proc_blocks = pd.read_parquet(blocks_path)

    block_features = (
        proc_blocks
        .groupby(["match_id", "player_id"])
        .size()
        .reset_index(name="blocks")
    )

    return block_features


def aggregate_interception_features(processed_dir):
    """
    Aggregates interception events to the player-match level.
    """
    print("Aggregating interception features...")

    interceptions_path = processed_dir / "interceptions.parquet"
    proc_interceptions = pd.read_parquet(interceptions_path)

    # Successful interception occurring in the attacking third
    proc_interceptions["poss_won_final_third"] = (
        proc_interceptions["interception_won"]
        & (proc_interceptions["x"] >= 80)
    )

    interception_features = (
        proc_interceptions
        .groupby(["match_id", "player_id"])
        .agg(
            interceptions=("player_id", "size"),
            interceptions_won=("interception_won", "sum"),
            poss_won_final_third_interceptions=(
                "poss_won_final_third",
                "sum",
            ),
        )
        .reset_index()
    )

    return interception_features


def aggregate_ball_recovery_features(processed_dir):
    """
    Aggregates ball recovery events to the player-match level.
    """
    print("Aggregating ball recovery features...")

    ball_recoveries_path = processed_dir / "ball_recoveries.parquet"
    proc_ball_recoveries = pd.read_parquet(ball_recoveries_path)

    ball_recovery_features = (
        proc_ball_recoveries
        .groupby(["match_id", "player_id"])
        .agg(
            ball_recoveries_attempted=("player_id", "size"),
            ball_recoveries_won=("ball_recovery_won", "sum"),
        )
        .reset_index()
    )

    return ball_recovery_features


def aggregate_pressure_features(processed_dir):
    """
    Aggregates pressure events to the player-match level.
    """
    print("Aggregating pressure features...")

    pressures_path = processed_dir / "pressures.parquet"
    proc_pressures = pd.read_parquet(pressures_path)

    pressure_features = (
        proc_pressures
        .groupby(["match_id", "player_id"])
        .size()
        .reset_index(name="pressures")
    )

    return pressure_features


def aggregate_foul_features(processed_dir):
    """
    Aggregates committed foul events to the player-match level.
    """
    print("Aggregating foul features...")

    fouls_path = processed_dir / "fouls.parquet"
    proc_fouls = pd.read_parquet(fouls_path)

    foul_features = (
        proc_fouls
        .groupby(["match_id", "player_id"])
        .size()
        .reset_index(name="fouls")
    )

    return foul_features


def is_progressive_action(x, y, end_x, end_y, threshold=0.25):
    """
    Determine whether a StatsBomb action is progressive.
    A progressive pass/carry must be completed and move the ball sufficiently closer to the center of the opponent's goal.

    StatsBomb coordinates:
        Pitch: 120 x 80
        Opponent goal center: (120, 40)

    Thresholds:
        Reduce distance to goal by at least 25%
    """

    goal_x, goal_y = 120, 40

    start_distance = np.hypot(
        goal_x - x,
        goal_y - y
    )

    end_distance = np.hypot(
        goal_x - end_x,
        goal_y - end_y
    )

    if start_distance == 0:
        return False

    progression = (
        start_distance - end_distance
    ) / start_distance

    return progression >= threshold


def is_progressive_pass(x, y, end_x, end_y, completed):
    """
    Determine whether a StatsBomb pass is progressive.
    A progressive pass must be completed and move the ball sufficiently closer to the center of the opponent's goal.

    StatsBomb coordinates:
        Pitch: 120 x 80
        Opponent goal center: (120, 40)

    Thresholds:
        Own half -> own half:          30 units
        Own half -> opponent half:     15 units
        Opponent half -> opponent half: 10 units
    """

    if not completed:
        return False

    goal_x, goal_y = 120, 40

    # Calculate distance to opponent's goal before and after pass
    start_distance = np.sqrt(
        (goal_x - x) ** 2 +
        (goal_y - y) ** 2
    )

    end_distance = np.sqrt(
        (goal_x - end_x) ** 2 +
        (goal_y - end_y) ** 2
    )

    distance_progressed = start_distance - end_distance

    # Own half -> own half
    if x < 60 and end_x < 60:
        return distance_progressed >= 30

    # Own half -> opponent half
    elif x < 60 and end_x >= 60:
        return distance_progressed >= 15

    # Opponent half -> opponent half
    elif x >= 60 and end_x >= 60:
        return distance_progressed >= 10

    # Opponent half -> own half cannot be progressive
    return False