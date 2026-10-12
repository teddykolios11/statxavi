from pathlib import Path
import pandas as pd

from utils import season_ids, top_league_comp_ids, pass_columns, dribble_columns, carry_columns, shot_columns, interception_columns, pressure_columns, duel_columns, clearance_columns, block_columns, ball_recovery_columns, foul_columns


def clean_season(competition_id, season_id):
    """
    Cleans the season data for a given competition and season.
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

    print(f"Cleaning data for competition: {competition}, season: {season}....")

    project_dir = Path(__file__).resolve().parent.parent

    raw_dir = project_dir / "data/raw" / competition / season
    processed_dir = project_dir / "data/processed" / competition / season

    processed_dir.mkdir(parents=True, exist_ok=True)

    events = load_raw_events(raw_dir)

    passes = clean_passes(events)
    dribbles = clean_dribbles(events)
    carries = clean_carries(events)
    shots = clean_shots(events)
    duels = clean_duels(events)
    clearances = clean_clearances(events)
    blocks = clean_blocks(events)
    interceptions = clean_interceptions(events)
    ball_recoveries = clean_ball_recoveries(events)
    pressures = clean_pressures(events)
    fouls = clean_fouls(events)
    player_minutes = calculate_player_minutes(events)

    passes.to_parquet(processed_dir / "passes.parquet", index=False)
    dribbles.to_parquet(processed_dir / "dribbles.parquet", index=False)
    carries.to_parquet(processed_dir / "carries.parquet", index=False)
    shots.to_parquet(processed_dir / "shots.parquet", index=False)
    duels.to_parquet(processed_dir / "duels.parquet", index=False)
    clearances.to_parquet(processed_dir / "clearances.parquet", index=False)
    blocks.to_parquet(processed_dir / "blocks.parquet", index=False)
    interceptions.to_parquet(processed_dir / "interceptions.parquet", index=False)
    ball_recoveries.to_parquet(processed_dir / "ball_recoveries.parquet", index=False)
    pressures.to_parquet(processed_dir / "pressures.parquet", index=False)
    fouls.to_parquet(processed_dir / "fouls.parquet", index=False)
    player_minutes.to_parquet(processed_dir / "player_minutes.parquet", index=False)

    print(f"Finished cleaning data for competition: {competition}, season: {season}.")


def load_raw_events(raw_dir):
    files = raw_dir.glob("*.parquet")

    return pd.concat(
        [pd.read_parquet(file) for file in files],
        ignore_index=True
    )


def clean_passes(events):
    passes = events[events["type"] == "Pass"].copy()
    passes = passes[pass_columns].reset_index(drop=True)

    print("Cleaning passes...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "pass_end_location",
    ]
    invalid_values = passes[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} pass events with missing required values"
        )

    # flag duplicate event IDs
    duplicates = passes["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} pass events with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    passes[["x", "y"]] = pd.DataFrame(
        passes["location"].tolist(),
        index=passes.index
    )
    passes[["end_x", "end_y"]] = pd.DataFrame(
        passes["pass_end_location"].tolist(),
        index=passes.index
    )
    passes = passes.drop(
        columns=["location", "pass_end_location"]
    )

    # assert valid integer and float values
    assert passes["x"].between(-1, 121).all()
    assert passes["y"].between(-1, 81).all()
    assert passes["end_x"].between(-1, 121).all()
    assert passes["end_y"].between(-1, 81).all()
    # assert passes["duration"].ge(0).all()
    # assert passes["pass_length"].between(0, 150).all()
    # assert passes["pass_angle"].between(-3.141593, 3.141593).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "pass_shot_assist",
        "pass_goal_assist",
        "pass_cross",
        "pass_cut_back",
        "pass_through_ball",
        "pass_switch",
        "under_pressure",
    ]
    passes[boolean_columns] = (
        passes[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag completed passes
    passes["completed"] = passes["pass_outcome"].isna()

    return passes


def clean_dribbles(events):
    dribbles = events[events["type"] == "Dribble"].copy()
    dribbles = dribbles[dribble_columns].reset_index(drop=True)

    print("Cleaning dribbles...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "dribble_outcome",
    ]
    invalid_values = dribbles[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} dribble events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = dribbles["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} dribble events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    dribbles[["x", "y"]] = pd.DataFrame(
        dribbles["location"].tolist(),
        index=dribbles.index
    )
    dribbles = dribbles.drop(columns=["location"])

    # assert valid integer and float values
    assert dribbles["x"].between(-1, 121).all()
    assert dribbles["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "dribble_nutmeg",
        "dribble_overrun",
        "under_pressure",
    ]
    dribbles[boolean_columns] = (
        dribbles[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag completed dribbles
    dribbles["dribble_completed"] = (
        dribbles["dribble_outcome"] == "Complete"
    )

    return dribbles


def clean_carries(events):
    carries = events[events["type"] == "Carry"].copy()
    carries = carries[carry_columns].reset_index(drop=True)

    print("Cleaning carries...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "carry_end_location",
    ]
    invalid_values = carries[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} carry events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = carries["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} carry events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    carries[["x", "y"]] = pd.DataFrame(
        carries["location"].tolist(),
        index=carries.index
    )
    carries[["end_x", "end_y"]] = pd.DataFrame(
        carries["carry_end_location"].tolist(),
        index=carries.index
    )
    carries = carries.drop(
        columns=["location", "carry_end_location"]
    )

    # assert valid integer and float values
    assert carries["x"].between(-1, 121).all()
    assert carries["y"].between(-1, 81).all()
    assert carries["end_x"].between(-1, 121).all()
    assert carries["end_y"].between(-1, 81).all()
    # assert carries["duration"].ge(0).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "under_pressure",
    ]
    carries[boolean_columns] = (
        carries[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    return carries


def clean_shots(events):
    shots = events[events["type"] == "Shot"].copy()
    shots = shots[shot_columns].reset_index(drop=True)

    print("Cleaning shots...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "shot_end_location",
        "shot_statsbomb_xg",
        "shot_outcome",
    ]
    invalid_values = shots[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} shot events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = shots["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} shot events "
            "with duplicate event IDs"
        )

    # split shot location
    shots[["x", "y"]] = pd.DataFrame(
        shots["location"].tolist(),
        index=shots.index
    )

    # split shot end location while preserving height
    shots["end_x"] = shots["shot_end_location"].str[0]
    shots["end_y"] = shots["shot_end_location"].str[1]
    shots["end_z"] = shots["shot_end_location"].str[2]

    shots = shots.drop(
        columns=["location", "shot_end_location"]
    )

    assert shots["x"].between(-1, 121).all()
    assert shots["y"].between(-1, 81).all()
    assert shots["end_x"].between(-1, 121).all()
    assert shots["end_y"].between(-1, 81).all()
    assert shots["shot_statsbomb_xg"].between(0, 1).all()
    assert shots["end_z"].dropna().ge(0).all()

    # normalize boolean flags
    boolean_columns = [
        "shot_first_time",
        "shot_one_on_one",
        "shot_open_goal",
        "under_pressure",
    ]
    shots[boolean_columns] = (
        shots[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag goals and on target shots
    shots["scored"] = (
        shots["shot_outcome"] == "Goal"
    )
    shots["on_target"] = shots["shot_outcome"].isin([
        "Goal",
        "Saved",
        "Saved to Post",
    ])

    return shots


def clean_duels(events):
    duels = events[events["type"] == "Duel"].copy()
    duels = duels[duel_columns].reset_index(drop=True)

    print("Cleaning duels...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "duel_type",
    ]
    invalid_values = duels[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} duel events "
            "with missing required values"
        )

    # assert outcome exists for tackle duel types
    tackles_missing_outcome = (
        duels["duel_type"].eq("Tackle")
        & duels["duel_outcome"].isna()
    )
    if tackles_missing_outcome.any():
        raise ValueError(
            f"Found {tackles_missing_outcome.sum()} tackle events "
            "with missing outcomes"
        )

    # flag duplicate event IDs
    duplicates = duels["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} duel events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    duels[["x", "y"]] = pd.DataFrame(
        duels["location"].tolist(),
        index=duels.index
    )
    duels = duels.drop(columns=["location"])

    # assert valid coordinates
    assert duels["x"].between(-1, 121).all()
    assert duels["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "counterpress",
    ]
    duels[boolean_columns] = (
        duels[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag tackles and successful tackle duels
    duels["tackle_attempted"] = duels["duel_type"].eq("Tackle")
    duels["tackle_won"] = (
        duels["tackle_attempted"]
        & duels["duel_outcome"].isin([
            "Won",
            "Success In Play",
            "Success Out",
        ])
    )

    return duels


def clean_clearances(events):
    clearances = events[events["type"] == "Clearance"].copy()

    # clearance_body_part missing in some competitions
    if "clearance_body_part" not in clearances.columns:
        clearances["clearance_body_part"] = pd.NA

    clearances = clearances[clearance_columns].reset_index(drop=True)

    print("Cleaning clearances...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
    ]
    invalid_values = clearances[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} clearance events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = clearances["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} clearance events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    clearances[["x", "y"]] = pd.DataFrame(
        clearances["location"].tolist(),
        index=clearances.index
    )
    clearances = clearances.drop(columns=["location"])

    # assert valid coordinates
    assert clearances["x"].between(-1, 121).all()
    assert clearances["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "clearance_aerial_won",
        "under_pressure",
    ]
    clearances[boolean_columns] = (
        clearances[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    return clearances


def clean_blocks(events):
    blocks = events[events["type"] == "Block"].copy()
    blocks = blocks[block_columns].reset_index(drop=True)

    print("Cleaning blocks...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
    ]
    invalid_values = blocks[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} block events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = blocks["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} block events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    blocks[["x", "y"]] = pd.DataFrame(
        blocks["location"].tolist(),
        index=blocks.index
    )
    blocks = blocks.drop(columns=["location"])

    # assert valid coordinates
    assert blocks["x"].between(-1, 121).all()
    assert blocks["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "block_offensive",
        "block_deflection",
        "block_save_block",
        "counterpress",
    ]
    blocks[boolean_columns] = (
        blocks[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    return blocks


def clean_interceptions(events):
    interceptions = events[events["type"] == "Interception"].copy()
    interceptions = interceptions[interception_columns].reset_index(drop=True)

    print("Cleaning interceptions...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
        "interception_outcome"
    ]
    invalid_values = interceptions[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} interception events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = interceptions["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} interception events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    interceptions[["x", "y"]] = pd.DataFrame(
        interceptions["location"].tolist(),
        index=interceptions.index
    )
    interceptions = interceptions.drop(columns=["location"])

    # assert valid coordinates
    assert interceptions["x"].between(-1, 121).all()
    assert interceptions["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "counterpress",
        "under_pressure",
    ]
    interceptions[boolean_columns] = (
        interceptions[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag successful interceptions
    interceptions["interception_won"] = interceptions["interception_outcome"].isin([
        "Won",
        "Success In Play",
        "Success Out",
    ])

    return interceptions


def clean_ball_recoveries(events):
    ball_recoveries = events[events["type"] == "Ball Recovery"].copy()
    ball_recoveries = ball_recoveries[ball_recovery_columns].reset_index(drop=True)

    print("Cleaning ball recoveries...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
    ]
    invalid_values = ball_recoveries[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} ball recovery events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = ball_recoveries["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} ball recovery events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    ball_recoveries[["x", "y"]] = pd.DataFrame(
        ball_recoveries["location"].tolist(),
        index=ball_recoveries.index
    )
    ball_recoveries = ball_recoveries.drop(columns=["location"])

    # assert valid coordinates
    assert ball_recoveries["x"].between(-1, 121).all()
    assert ball_recoveries["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "ball_recovery_offensive",
        "ball_recovery_recovery_failure",
        "under_pressure",
    ]
    ball_recoveries[boolean_columns] = (
        ball_recoveries[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    # flag successful ball recoveries
    ball_recoveries["ball_recovery_won"] = (
        ~ball_recoveries["ball_recovery_recovery_failure"]
        .fillna(False)
        .astype(bool)
    )

    return ball_recoveries


def clean_pressures(events):
    pressures = events[events["type"] == "Pressure"].copy()
    pressures = pressures[pressure_columns].reset_index(drop=True)

    print("Cleaning pressures...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
    ]
    invalid_values = pressures[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} pressure events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = pressures["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} pressure events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    pressures[["x", "y"]] = pd.DataFrame(
        pressures["location"].tolist(),
        index=pressures.index
    )
    pressures = pressures.drop(columns=["location"])

    # assert valid coordinates and duration
    assert pressures["x"].between(-1, 121).all()
    assert pressures["y"].between(-1, 81).all()
    # assert pressures["duration"].ge(0).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "counterpress",
    ]
    pressures[boolean_columns] = (
        pressures[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    return pressures


def clean_fouls(events):
    fouls = events[events["type"] == "Foul Committed"].copy()
    fouls = fouls[foul_columns].reset_index(drop=True)

    print("Cleaning fouls...")

    # ensure required values are present
    required_values = [
        "match_id",
        "id",
        "player_id",
        "team_id",
        "location",
    ]
    invalid_values = fouls[required_values].isna().any(axis=1)
    if invalid_values.any():
        raise ValueError(
            f"Found {invalid_values.sum()} foul events "
            "with missing required values"
        )

    # flag duplicate event IDs
    duplicates = fouls["id"].duplicated(keep=False)
    if duplicates.any():
        raise ValueError(
            f"Found {duplicates.sum()} foul events "
            "with duplicate event IDs"
        )

    # convert location cols from tuple to separate x/y columns
    fouls[["x", "y"]] = pd.DataFrame(
        fouls["location"].tolist(),
        index=fouls.index
    )
    fouls = fouls.drop(columns=["location"])

    # assert valid coordinates
    assert fouls["x"].between(-1, 121).all()
    assert fouls["y"].between(-1, 81).all()

    # convert boolean columns to bool type
    boolean_columns = [
        "foul_committed_advantage",
        "foul_committed_offensive",
        "foul_committed_penalty",
        "counterpress",
    ]
    fouls[boolean_columns] = (
        fouls[boolean_columns]
        .fillna(False)
        .astype(bool)
    )

    return fouls


def get_period_durations(events):
    """
    Returns actual duration of each match period.
    """

    period_ends = events[events["type"] == "Half End"].copy()

    period_ends["_period_seconds"] = (
        pd.to_timedelta(period_ends["timestamp"])
        .dt.total_seconds()
    )

    return (
        period_ends
        .groupby(["match_id", "period"])["_period_seconds"]
        .max()
        .to_dict()
    )


def get_absolute_event_time(row, period_durations):
    """
    Converts a period-relative timestamp into seconds since the beginning of the match.
    """

    match_id = row["match_id"]
    period = row["period"]

    period_start = sum(
        period_durations[(match_id, previous_period)]
        for previous_period in range(1, period)
    )
    timestamp = pd.to_timedelta(row["timestamp"]).total_seconds()

    return float(period_start + timestamp)


def calculate_player_minutes(events):
    """
    Reconstructs player participation intervals using Starting XI, Substitution, and dismissal events.
    """
    print("Calculating player minutes...")

    # Get the actual duration of every period for every match.
    period_durations = get_period_durations(events)
    
    # Filter to only include events relevant to minutes calculations
    relevant_types = [
        "Starting XI",
        "Substitution",
        "Bad Behaviour",
        "Foul Committed",
    ]

    # player_off_permanent field missing for some competitions, set to False in case
    player_off_permanent = (
        events["player_off_permanent"].fillna(False)
        if "player_off_permanent" in events.columns
        else pd.Series(False, index=events.index)
    )
    timed_events = events[
        events["type"].isin(relevant_types)
        | player_off_permanent.eq(True)
    ].copy()

    # Add a continuous match clock to each event.
    timed_events["_absolute_time"] = timed_events.apply(
        get_absolute_event_time,
        axis=1,
        period_durations=period_durations,
    )

    # Temporary store player participation records by: (match_id, player_id)
    players = {}

    for match_id, match_events in timed_events.groupby("match_id", sort=False):

        # Compute total duration of each match
        match_id = int(match_id)
        match_duration = sum(
            duration
            for (duration_match_id, _), duration in period_durations.items()
            if duration_match_id == match_id
        )

        # INITIALIZE STARTERS

        starting_xi = match_events[
            match_events["type"] == "Starting XI"
        ]

        # Each team has one Starting XI event - players are stored inside nested tactics["lineup"] field.
        for _, row in starting_xi.iterrows():
            for lineup_player in row["tactics"]["lineup"]:
                player_info = lineup_player["player"]
                player_id = int(player_info["id"])

                players[(match_id, player_id)] = {
                    "match_id": match_id,
                    "player_id": player_id,
                    "player": player_info["name"],
                    "team_id": int(row["team_id"]),
                    "team": row["team"],
                    "started": True,
                    "time_on": 0.0, # Starters enter at beginning of the match
                    "time_off": float(match_duration), # Assume full match play unless later sub/dismissals change this
                }

        # Process events chronologically so participation records are updated in the same order events occurred.
        for _, row in (
            match_events
            .sort_values("_absolute_time")
            .iterrows()
        ):
            event_time = float(row["_absolute_time"])

            # HANDLING SUBSTITUTIONS

            if row["type"] == "Substitution":

                # Player field identifies player leaving.
                outgoing_id = int(row["player_id"])
                outgoing_key = (match_id, outgoing_id)
                players[outgoing_key]["time_off"] = event_time

                # The substitution_replacement field identifies the player entering the match.
                replacement_id = int(
                    row["substitution_replacement_id"]
                )

                replacement_key = (match_id, replacement_id)
                players[replacement_key] = {
                    "match_id": match_id,
                    "player_id": replacement_id,
                    "player": row["substitution_replacement"],
                    "team_id": int(row["team_id"]),
                    "team": row["team"],
                    "started": False,
                    "time_on": event_time,
                    "time_off": float(match_duration), # Assume sub finishes match unless later event changes
                }

            # HANDLING DISMISSALS

            # Red cards can be recorded on Bad Behaviour or Foul Committed events.
            dismissal_cards = {"Red Card", "Second Yellow"}
            dismissal = (
                row.get("player_off_permanent") == True
                or row.get("bad_behaviour_card") in dismissal_cards
                or row.get("foul_committed_card") in dismissal_cards
            )

            # If this event represents a dismissal, stop counting minutes for that player.
            if dismissal:
                dismissed_id = int(row["player_id"])
                dismissed_key = (match_id, dismissed_id)

                # Only process the dismissal if the player has participated in the match.
                if dismissed_key in players:
                    players[dismissed_key]["time_off"] = min(
                        players[dismissed_key]["time_off"],
                        event_time
                    )

    # CONVERT RECORDS TO DATAFRAME

    result = pd.DataFrame(players.values())

    # Calculate final minutes played from the reconstructed interval.
    result["minutes_played"] = (
        result["time_off"] - result["time_on"]
    ) / 60

    return result