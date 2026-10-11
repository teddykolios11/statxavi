from pathlib import Path
from statsbombpy import sb
import pandas as pd
import warnings

warnings.filterwarnings(
    "ignore",
    message="credentials were not supplied.*"
)

from utils import season_ids, top_league_comp_ids, POSITION_GROUPS


def ingest_matches(competition_id, season_id):
    """
    Ingests matches for a given competition and season.
    """

    matches = sb.matches(
        competition_id=competition_id,
        season_id=season_id,
    )

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

    print(f"Ingesting matches for competition: {competition}, season: {season}....")
    print(f"Found {len(matches)} matches for competition: {competition}, season: {season}....")

    data_dir = Path(__file__).resolve().parent.parent / "data/raw"
    match_dir = data_dir / competition / season

    for match_id in matches["match_id"]:
        match_path = match_dir / f"{match_id}.parquet"

        if match_path.exists():
            print(f"\tSkipping match_id {match_id} — already exists.")
            continue

        print(f"\tIngesting event data for match_id: {match_id}...")
        events = sb.events(match_id=match_id)
        match_dir.mkdir(parents=True, exist_ok=True)
        events.to_parquet(match_dir / f"{str(match_id)}.parquet", index=False)


def ingest_player_season_positions(competition_id, season_id):
    """
    Determine each player's most commonly played position
    for a given competition and season.
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

    print(f"Ingesting player positions for competition: {competition}, season: {season}...")

    project_dir = Path(__file__).resolve().parent.parent
    processed_dir = project_dir / "data/processed" / competition / season

    processed_dir.mkdir(parents=True, exist_ok=True)

    # Get all matches for competition-season
    matches = sb.matches(
        competition_id=competition_id,
        season_id=season_id
    )

    rows = []

    # Collect every position recorded for every player
    for match_id in matches["match_id"]:

        lineups = sb.lineups(match_id=match_id)

        for team_name, lineup in lineups.items():
            for _, player in lineup.iterrows():
                positions = player["positions"]

                if not positions:
                    continue

                initial_position = positions[0]

                rows.append({
                    "player_id": player["player_id"],
                    "player": player["player_name"],
                    "season": season,
                    "position": initial_position["position"]
                })

    positions_df = pd.DataFrame(rows)

    # Count how often each player appears at each position
    position_counts = (
        positions_df
        .groupby(
            ["player_id", "player", "season", "position"],
            as_index=False
        )
        .size()
        .rename(columns={"size": "position_appearances"})
    )

    # Most frequently occurring position = primary position
    primary_positions = (
        position_counts
        .sort_values(
            ["player_id", "position_appearances"],
            ascending=[True, False]
        )
        .drop_duplicates("player_id")
        .rename(columns={"position": "primary_position"})
    )

    # Map detailed StatsBomb position to broader group
    primary_positions["position_group"] = (
        primary_positions["primary_position"]
        .map(POSITION_GROUPS)
    )

    primary_positions = primary_positions[[
        "player_id",
        "player",
        "season",
        "primary_position",
        "position_group"
    ]]

    # Save completed player positions table
    output_path = processed_dir / "player_positions.parquet"
    primary_positions.to_parquet(output_path, index=False)

    print(f"Saved {len(primary_positions):,} player position rows to {output_path}")