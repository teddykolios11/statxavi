from pathlib import Path

import pandas as pd
import numpy as np
import json
import pickle

from fastapi import FastAPI, HTTPException

from src.modeling.similarity import find_similar_players
from src.utils import PCA_FEATURE_COLUMNS, PCA_N_COMPONENTS


app = FastAPI(
    title="StatsBomb Player Similarity API",
    version="1.0.0",
)

project_dir = Path(__file__).resolve().parent.parent.parent

AVAILABLE_SEASONS = [
    "2015-2016",
    "2018",
    "2020",
    "2022",
    "2024",
]

DEFAULT_SEASON = "2015-2016"


def load_season_data(season):
    model_dir = project_dir / "data" / "model" / season
    pca_dir = project_dir / "models" / "pca" / season

    with (pca_dir / "scaler.pkl").open("rb") as file:
        scaler = pickle.load(file)

    with (pca_dir / "metadata.json").open("r") as file:
        metadata = json.load(file)

    return {
        "features": pd.read_parquet(
            model_dir / "pca_features.parquet"
        ),
        "percentiles": pd.read_parquet(
            model_dir / "percentile_features.parquet"
        ),
        "position_percentiles": pd.read_parquet(
            model_dir / "position_percentile_features.parquet"
        ),
        "scores": pd.read_parquet(
            pca_dir / "player_scores.parquet"
        ),
        "scaler": scaler,
        "metadata": metadata,
    }

season_data = {
    season: load_season_data(season)
    for season in AVAILABLE_SEASONS
}


def get_season_data(season):
    if season not in season_data:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid season: {season}. "
                   f"Available seasons: {AVAILABLE_SEASONS}"
        )

    return season_data[season]


@app.get("/players/pca-map")
def get_pca_map(season: str = DEFAULT_SEASON):
    player_scores = get_season_data(season)["scores"]

    pc_cols = [f"PC{i}" for i in range(1, PCA_N_COMPONENTS + 1)]

    columns = [
        "player_id",
        "player",
        "teams",
        "position_group",
    ] + pc_cols

    pca_map_scores = player_scores[columns].copy()

    pca_map_scores["teams"] = pca_map_scores["teams"].apply(
        lambda value: value.tolist()
        if isinstance(value, np.ndarray)
        else value
    )

    return pca_map_scores.to_dict(orient="records")


@app.get("/players/{player_name}/similar")
def get_similar_players(
    player_name: str,
    n_neighbors: int = 5,
    position_group: str | None = None,
    season: str = DEFAULT_SEASON,
):
    try:
        season_data = get_season_data(season)
        player_scores = season_data["scores"] # get PCA results for selected season
        median_distance = season_data["metadata"]["pca"]["median_pairwise_distance"]
        results = find_similar_players(
            player_name=player_name,
            player_scores=player_scores,
            median_pairwise_distance=median_distance,
            n_neighbors=n_neighbors,
            position_group=position_group,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    results["teams"] = results["teams"].apply(
        lambda value: value.tolist()
        if isinstance(value, np.ndarray)
        else value
    )

    return results.to_dict(orient="records")


@app.get("/players/{player_name}/feature_differences")
def get_feature_differences(
    player_name: str,
    comparison_player: str,
    season: str = DEFAULT_SEASON,
):
    season_data = get_season_data(season)
    player_features = season_data["features"]
    scaler = season_data["scaler"]

    # Retrieve both players
    player_a = player_features.loc[player_features["player"] == player_name]
    player_b = player_features.loc[player_features["player"] == comparison_player]

    if player_a.empty or player_b.empty:
        raise HTTPException(status_code=404, detail="Player not found")

    # Use the exact features and order from the fitted scaler
    feature_cols = list(PCA_FEATURE_COLUMNS)

    # Standardize using the existing fitted scaler
    a_scaled = scaler.transform(player_a[feature_cols])[0]
    b_scaled = scaler.transform(player_b[feature_cols])[0]

    # Calculate feature-level differences
    differences = []

    for feature, a, b in zip(feature_cols, a_scaled, b_scaled):
        differences.append({
            "feature": feature,
            "player_a_z": round(float(a), 3),
            "player_b_z": round(float(b), 3),
            "difference": round(float(a - b), 3),
            "absolute_difference": round(float(abs(a - b)), 3),
        })

    # Most similar features first
    differences.sort(key=lambda item: item["absolute_difference"])

    return {
        "player_a": player_name,
        "player_b": comparison_player,
        "season": season,
        "differences": differences,
    }


@app.get("/players/{player_name}/info")
def get_player_info(player_name: str, season: str = DEFAULT_SEASON):
    player_features = get_season_data(season)["features"]
    player_matches = player_features.loc[
        player_features["player"].str.casefold().eq(player_name.casefold())
    ]

    if player_matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Player not found: {player_name}",
        )

    player = player_matches.iloc[0]
    teams = player["teams"]
    if isinstance(teams, np.ndarray):
        teams = teams.tolist()

    return {
        "player": player["player"],
        "competition": player["competition"],
        "team": teams,
        "matches_played": int(player["matches_played"]),
        "starts": int(player["starts"]),
        "minutes_played": int(player["minutes_played"]),
        "primary_position": player["primary_position"],
        "position_group": player["position_group"],
    }


@app.get("/players/{player_name}/percentiles")
def get_player_percentiles(player_name: str, season: str = DEFAULT_SEASON):
    player_percentiles = get_season_data(season)["percentiles"]
    player_matches = player_percentiles.loc[
        player_percentiles["player"].str.casefold().eq(player_name.casefold())
    ]

    if player_matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Player not found: {player_name}",
        )

    player = player_matches.iloc[0]
    teams = player["teams"]
    if isinstance(teams, np.ndarray):
        teams = teams.tolist()

    return {
        "player": player["player"],
        "team": teams,
        "position": player["primary_position"],
        "percentiles": {
            column: float(player[column])
            for column in PCA_FEATURE_COLUMNS
        },
    }


@app.get("/players/{player_name}/position_percentiles")
def get_player_position_percentiles(player_name: str, season: str = DEFAULT_SEASON):
    player_position_percentiles = get_season_data(season)["position_percentiles"]
    player_matches = player_position_percentiles.loc[
        player_position_percentiles["player"].str.casefold().eq(player_name.casefold())
    ]

    if player_matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Player not found: {player_name}",
        )

    player = player_matches.iloc[0]
    teams = player["teams"]
    if isinstance(teams, np.ndarray):
        teams = teams.tolist()

    return {
        "player": player["player"],
        "team": teams,
        "position": player["primary_position"],
        "percentiles": {
            column: float(player[column])
            for column in PCA_FEATURE_COLUMNS
        },
    }


@app.get("/players/{player_name}/features")
def get_player_features(player_name: str, season: str = DEFAULT_SEASON):
    player_features = get_season_data(season)["features"]
    player_matches = player_features.loc[
        player_features["player"].str.casefold().eq(player_name.casefold())
    ]

    if player_matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Player not found: {player_name}",
        )

    player = player_matches.iloc[0]
    teams = player["teams"]
    if isinstance(teams, np.ndarray):
        teams = teams.tolist()

    return {
        "player": player["player"],
        "team": teams,
        "position": player["primary_position"],
        "features": {
            column: float(player[column])
            for column in PCA_FEATURE_COLUMNS
        },
    }


@app.get("/players")
def search_players(query: str, season: str = DEFAULT_SEASON):
    player_scores = get_season_data(season)["scores"]

    player_matches = player_scores.loc[
        player_scores["player"].str.contains(
            query,
            case=False,
            na=False,
        ),
        [
            "player",
            "teams",
            "primary_position",
        ],
    ].copy()

    player_matches["teams"] = player_matches["teams"].apply(
        lambda value: value.tolist()
        if isinstance(value, np.ndarray)
        else value
    )

    player_matches = (
        player_matches
        .drop_duplicates(subset=["player"])
        .head(10)
    )

    return player_matches.to_dict(orient="records")


@app.get("/seasons")
def get_available_seasons():
    return {
        "seasons": [
            {"id": "2015-2016", "label": "2015/16 European Leagues"},
            {"id": "2018", "label": "2018 FIFA World Cup"},
            {"id": "2020", "label": "2020 UEFA Euro"},
            {"id": "2022", "label": "2022 FIFA World Cup"},
            {"id": "2024", "label": "2024 UEFA Euro"},
        ],
        "default": DEFAULT_SEASON,
    }