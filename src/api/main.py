from pathlib import Path

import pandas as pd
import numpy as np

from fastapi import FastAPI, HTTPException

from src.modeling.similarity import find_similar_players
from src.utils import PCA_FEATURE_COLUMNS


app = FastAPI(
    title="StatsBomb Player Similarity API",
    version="1.0.0",
)

project_dir = Path(__file__).resolve().parent.parent.parent

features_path = (
    project_dir
    / "data"
    / "model"
    / "2015-2016"
    / "pca_features.parquet"
)
percentiles_path = (
    project_dir
    / "data"
    / "model"
    / "2015-2016"
    / "percentile_features.parquet"
)
position_percentiles_path = (
    project_dir
    / "data"
    / "model"
    / "2015-2016"
    / "position_percentile_features.parquet"
)
scores_path = (
    project_dir
    / "models"
    / "pca"
    / "2015-2016"
    / "player_scores.parquet"
)

player_features = pd.read_parquet(features_path)
player_percentiles = pd.read_parquet(percentiles_path)
player_position_percentiles = pd.read_parquet(position_percentiles_path)
player_scores = pd.read_parquet(scores_path)


@app.get("/players/{player_name}/similar")
def get_similar_players(
    player_name: str,
    n_neighbors: int = 5,
    position_group: str | None = None,
):
    try:
        results = find_similar_players(
            player_name=player_name,
            player_scores=player_scores,
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


@app.get("/players/{player_name}/info")
def get_player_info(player_name: str):
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
def get_player_percentiles(player_name: str):
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
def get_player_position_percentiles(player_name: str):
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
def get_player_features(player_name: str):
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
def search_players(query: str):
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