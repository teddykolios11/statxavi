import pickle
import json
from pathlib import Path

import numpy as np
import pandas as pd

import mlflow

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import trustworthiness
from sklearn.metrics.pairwise import euclidean_distances
from scipy.spatial.distance import pdist

from utils import season_ids, top_league_comp_ids, PCA_VOLUME_COLUMNS, PCA_FEATURE_COLUMNS, PCA_N_COMPONENTS


def build_pca_features(season_id, min_minutes=600):
    """
    Build and save model-ready player features across competitions for a season.

    Filters players by minimum minutes played, converts volume metrics
    to per-90 rates, and retains the selected PCA features and metadata.
    """

    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    if min_minutes < 0:
        raise ValueError("min_minutes must be non-negative")

    project_dir = Path(__file__).resolve().parent.parent.parent
    volume_columns = list(PCA_VOLUME_COLUMNS)
    feature_columns = list(PCA_FEATURE_COLUMNS)

    required_columns = [
        "competition_id",
        "competition",
        "season_id",
        "season",
        "player_id",
        "player",
        "team_ids",
        "teams",
        "matches_played",
        "starts",
        "minutes_played",
        "primary_position",
        "position_group",
        "pass_completion_pct",
        *volume_columns,
    ]

    # Load and combine player-season feature tables from all available competitions.
    player_season_tables = []
    missing_competitions = []
    for competition in top_league_comp_ids:
        input_path = (project_dir / "data" / "processed" / competition / season / "player_season_features.parquet")
        if not input_path.is_file():
            missing_competitions.append(competition)
            continue

        player_seasons = pd.read_parquet(input_path)
        missing_columns = sorted(
            set(required_columns) - set(player_seasons.columns)
        )
        if missing_columns:
            raise ValueError(
                f"Player-season features at {input_path} are missing required columns: " + ", ".join(missing_columns)
            )
        if not player_seasons["season_id"].eq(season_id).all():
            raise ValueError(
                f"Unexpected season_id found in {input_path}"
            )

        player_season_tables.append(player_seasons)

    if not player_season_tables:
        raise FileNotFoundError(
            f"No player-season feature files found for season_id={season_id}"
        )
    if missing_competitions:
        print(
            "No player-season feature files found for: " + ", ".join(missing_competitions)
        )

    player_seasons = pd.concat(player_season_tables, ignore_index=True)

    # Restrict the modeling pool to players with sufficient playing time.
    filtered = player_seasons.loc[player_seasons["minutes_played"] >= min_minutes].copy()
    if filtered.empty:
        raise ValueError(
            f"No players meet the minimum playing-time threshold "
            f"of {min_minutes} minutes"
        )

    # Convert season volume metrics to per-90 rates.
    for column in volume_columns:
        filtered[f"{column}_per90"] = np.where(
            filtered["minutes_played"] > 0,
            filtered[column] / filtered["minutes_played"] * 90,
            np.nan,
        )

    player_metadata_columns = [
        "competition_id",
        "competition",
        "season_id",
        "season",
        "player_id",
        "player",
        "team_ids",
        "teams",
        "matches_played",
        "starts",
        "minutes_played",
        "primary_position",
        "position_group",
    ]

    pca_features = filtered[player_metadata_columns + feature_columns].copy()

    # PCA requires a complete, finite feature matrix.
    feature_values = pca_features[feature_columns].to_numpy()
    if not np.isfinite(feature_values).all():
        raise ValueError(
            "PCA features contain missing or infinite values"
        )

    # Each row should represent one player-competition-season observation.
    duplicate_mask = pca_features.duplicated(
        subset=["competition_id", "season_id", "player_id"], keep=False
    )
    if duplicate_mask.any():
        duplicates = pca_features.loc[
            duplicate_mask,
            ["competition", "player", "player_id"]
        ]
        raise ValueError(
            "Duplicate player-competition-season rows found:\n" + duplicates.to_string(index=False)
        )

    # Save PCA features for eventual model fitting
    output_dir = project_dir / "data" / "model" / season
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "pca_features.parquet"
    pca_features.to_parquet(output_path, index=False)

    # Persist feature-generation metadata for reproducibility and downstream model fitting.
    metadata = {
        "season_id": int(season_id),
        "season": season,
        "min_minutes": min_minutes,
        "n_players": len(pca_features),
        "n_features": len(feature_columns),
        "features": feature_columns,
        "competitions": sorted(
            pca_features["competition"].unique().tolist()
        ),
    }
    metadata_path = output_dir / "metadata.json"
    with metadata_path.open("w") as file:
        json.dump(metadata, file, indent=4)

    print(f"Saved {len(pca_features):,} PCA feature rows to {output_path}")
    print(f"Saved PCA feature metadata to {metadata_path}")

    return output_path


def calculate_player_percentiles(season_id):
    """
    Calculate population-wide percentile ranks for player statistical features.
    """

    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    project_dir = Path(__file__).resolve().parent.parent.parent
    features_dir = project_dir / "data" / "model" / season
    features_path = features_dir / "pca_features.parquet"
    player_features = pd.read_parquet(features_path)

    feature_columns = list(PCA_FEATURE_COLUMNS)
    player_features[feature_columns] = (
        player_features[feature_columns].rank(method="average", pct=True) * 100
    )

    output_path = features_dir / "percentile_features.parquet"
    player_features.to_parquet(output_path, index=False)

    print(f"Saved {len(player_features):,} percentile feature rows to {output_path}")
    return output_path


def calculate_player_position_percentiles(season_id):
    """
    Calculate position-group-specific percentile ranks for player statistical features.
    """

    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    project_dir = Path(__file__).resolve().parent.parent.parent
    features_dir = project_dir / "data" / "model" / season
    features_path = features_dir / "pca_features.parquet"
    player_features = pd.read_parquet(features_path)

    feature_columns = list(PCA_FEATURE_COLUMNS)
    player_features[feature_columns] = (
        player_features.groupby("position_group")[feature_columns]
        .rank(method="average", pct=True) * 100
    )

    output_path = features_dir / "position_percentile_features.parquet"
    player_features.to_parquet(output_path, index=False)

    print(f"Saved {len(player_features):,} position percentile feature rows to {output_path}")
    return output_path


def fit_pca(season_id, n_components=PCA_N_COMPONENTS, save_artifacts=True):
    """
    Fit a StandardScaler and PCA model and save the fitted artifacts,
    player component scores, loadings, and explained variance across
    competitions for the season.
    """

    seasons_by_id = {value: key for key, value in season_ids.items()}

    try:
        season = seasons_by_id[season_id].replace("/", "-")
    except KeyError as exc:
        raise ValueError(f"Unknown season_id: {season_id}") from exc

    project_dir = Path(__file__).resolve().parent.parent.parent
    features_dir = project_dir / "data" / "model" / season

    features_path = features_dir / "pca_features.parquet"
    metadata_path = features_dir / "metadata.json"

    player_features = pd.read_parquet(features_path)

    # Load feature-generation metadata and verify the fitting configuration.
    with metadata_path.open("r") as file:
        metadata = json.load(file)

    feature_columns = list(PCA_FEATURE_COLUMNS)
    feature_data = player_features[feature_columns]

    feature_values = feature_data.to_numpy(dtype=float)

    # Standardize features so differently scaled metrics contribute comparably to PCA.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_values)

    # Fit all available components; component selection is handled downstream.
    pca = PCA(n_components=n_components)
    player_coordinates = pca.fit_transform(scaled_features)

    component_columns = [
        f"PC{i}" for i in range(1, pca.n_components_ + 1)
    ]

    # Store each player's coordinates in PCA space alongside their metadata.
    player_metadata_columns = [
        column for column in player_features.columns
        if column not in feature_columns
    ]
    player_scores = player_features[player_metadata_columns].copy()
    player_scores[component_columns] = player_coordinates

    # Store PCA diagnostics for downstream analysis.
    explained_variance = pd.DataFrame(
        {
            "component": component_columns,
            "explained_variance": pca.explained_variance_,
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "cumulative_explained_variance_ratio": np.cumsum(
                pca.explained_variance_ratio_
            ),
        }
    )

    loadings = (
        pd.DataFrame(
            pca.components_.T,
            index=feature_columns,
            columns=component_columns,
        )
        .rename_axis("feature")
        .reset_index()
    )

    # calculate median similarity distance for downstream similarity score
    median_pairwise_distance = float(
        np.median(pdist(player_coordinates, metric="euclidean"))
    )
    if median_pairwise_distance <= 0:
        raise ValueError(
            "Median pairwise distance must be positive."
        )

    metadata["pca"] = {
        "n_components": int(pca.n_components_),
        "original_n_features": len(feature_columns),
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "cumulative_explained_variance_ratio": np.cumsum(
            pca.explained_variance_ratio_
        ).tolist(),
        "total_explained_variance_ratio": float(
            np.sum(pca.explained_variance_ratio_)
        ),
        "median_pairwise_distance": median_pairwise_distance
    }

    # Save fitted models and analysis-ready outputs.
    if save_artifacts:
        output_dir = project_dir / "models" / "pca" / season
        output_dir.mkdir(parents=True, exist_ok=True)

        player_scores.to_parquet(
            output_dir / "player_scores.parquet",
            index=False,
        )
        explained_variance.to_parquet(
            output_dir / "explained_variance.parquet",
            index=False,
        )
        loadings.to_parquet(
            output_dir / "loadings.parquet",
            index=False,
        )

        with (output_dir / "scaler.pkl").open("wb") as file:
            pickle.dump(scaler, file)

        with (output_dir / "pca.pkl").open("wb") as file:
            pickle.dump(pca, file)

        with (output_dir / "metadata.json").open("w") as file:
            json.dump(metadata, file, indent=4)

        print(
            f"Fitted PCA on {len(player_features):,} players and "
            f"{len(feature_columns)} features."
        )
        print(f"Saved PCA artifacts to {output_dir}")

    return scaled_features, player_scores, explained_variance, loadings


def run_pca_experiment(
    season_id,
    player_scores,
    standardized_features,
    explained_variance,
    n_components,
    n_neighbors=5,
    min_minutes=600,
):
    run_name = f"pca_{n_components}_components"
    print(
        f"Starting PCA experiment: {run_name} "
        f"(season_id={season_id}, min_minutes={min_minutes}, "
        f"n_neighbors={n_neighbors})..."
    )

    with mlflow.start_run(run_name=run_name):
        # Experiment configuration
        mlflow.log_params({
            "season_id": season_id,
            "min_minutes": min_minutes,
            "n_components": n_components,
            "n_neighbors": n_neighbors,
            "n_features": standardized_features.shape[1],
            "n_players": standardized_features.shape[0],
        })

        # Evaluate PCA representation
        results = evaluate_pca_model(
            player_scores=player_scores,
            standardized_features=standardized_features,
            explained_variance=explained_variance,
            n_neighbors=n_neighbors,
            n_components=n_components,
        )

        # Evaluation results
        metrics = {
            key: value
            for key, value in results.items()
            if value is not None
        }

        mlflow.log_metrics(metrics)

        mlflow.set_tags({
            "model_type": "PCA",
            "project": "statsbomb-player-similarity",
        })

        print("Evaluation results:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")

        print(f"Logged experiment '{run_name}' to MLflow.")

        return results


def evaluate_pca_model(
    player_scores,
    standardized_features,
    explained_variance,
    n_neighbors=5,
    n_components=6,
):
    """
    Evaluate the quality of a PCA representation.

    Measures cumulative explained variance, trustworthiness, top-k
    neighbor preservation, and position-group consistency for the
    selected number of principal components.

    ``standardized_features`` must be the exact standardized feature
    matrix used to fit PCA, with rows aligned to ``player_scores``.
    """
    standardized_features = np.asarray(standardized_features, dtype=float)
    _validate_evaluation_inputs(
        player_scores,
        standardized_features,
        n_neighbors,
        n_components,
    )
    pc_columns = [f"PC{i}" for i in range(1, n_components + 1)]
    component_scores = player_scores[pc_columns].to_numpy(dtype=float)

    return {
        "cumulative_explained_variance_ratio": _calculate_cumulative_explained_variance(
            explained_variance,
            n_components,
        ),
        "trustworthiness": _calculate_trustworthiness(
            standardized_features,
            component_scores,
            n_neighbors,
        ),
        "top_k_neighbor_preservation": _calculate_top_k_neighbor_preservation(
                standardized_features,
                component_scores,
                n_neighbors,
        ),
        "position_group_consistency": _calculate_position_group_consistency(
                player_scores,
                component_scores,
                n_neighbors,
        ),
    }


def _distance_matrix(values):
    distances = euclidean_distances(values)
    np.fill_diagonal(distances, np.inf)
    return distances


def _calculate_top_k_neighbor_preservation(
    standardized_features,
    component_scores,
    n_neighbors,
):
    original_neighbors = np.argsort(
        _distance_matrix(standardized_features),
        axis=1,
        kind="stable",
    )[:, :n_neighbors]
    component_neighbors = np.argsort(
        _distance_matrix(component_scores),
        axis=1,
        kind="stable",
    )[:, :n_neighbors]
    preservation_by_player = [
        len(set(original) & set(reduced)) / n_neighbors
        for original, reduced in zip(original_neighbors, component_neighbors)
    ]
    return float(np.mean(preservation_by_player))


def _calculate_trustworthiness(
    standardized_features,
    component_scores,
    n_neighbors,
):
    return float(
        trustworthiness(
            standardized_features,
            component_scores,
            n_neighbors=n_neighbors,
        )
    )


def _calculate_position_group_consistency(
    player_scores,
    component_scores,
    n_neighbors,
):
    neighbor_indices = np.argsort(
        _distance_matrix(component_scores),
        axis=1,
        kind="stable",
    )[:, :n_neighbors]

    position_groups = player_scores["position_group"].to_numpy()

    valid_target_indices = np.flatnonzero(pd.notna(position_groups))
    if len(valid_target_indices) == 0:
        return None

    consistency_by_player = []
    for target_idx in valid_target_indices:
        neighbor_groups = position_groups[
            neighbor_indices[target_idx]
        ]

        valid_neighbors = pd.notna(neighbor_groups) # ignore neighbors with missing position groups
        if not valid_neighbors.any():
            continue

        target_group = position_groups[target_idx]
        consistency = np.mean(
            neighbor_groups[valid_neighbors] == target_group
        )
        consistency_by_player.append(consistency)

    if not consistency_by_player:
        return None
    
    return float(np.mean(consistency_by_player))


def _calculate_cumulative_explained_variance(explained_variance, n_components):
    component = f"PC{n_components}"
    matching_rows = explained_variance.loc[
        explained_variance["component"].eq(component),
        "cumulative_explained_variance_ratio",
    ]
    if matching_rows.empty:
        raise ValueError(
            f"Explained-variance data does not include {component}"
        )
    return float(matching_rows.iloc[0])


def _validate_evaluation_inputs(
    player_scores,
    standardized_features,
    n_neighbors,
    n_components,
):
    if n_neighbors < 1:
        raise ValueError("n_neighbors must be at least 1")
    if n_neighbors >= len(player_scores) / 2:
        raise ValueError(
            "n_neighbors must be less than half the number of player rows"
        )
    
    if not 1 <= n_components <= standardized_features.shape[1]:
        raise ValueError(
            "n_components must be between 1 and the number of original features"
        )

    if standardized_features.shape[0] != len(player_scores):
        raise ValueError(
            "standardized_features must have one row per player_scores row in the same order"
        )