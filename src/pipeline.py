import argparse
import mlflow

from ingest import ingest_matches, ingest_player_season_positions
from clean import clean_season
from features import build_player_match_features, build_player_season_features
from modeling.pca import build_pca_features, calculate_player_percentiles, calculate_player_position_percentiles, fit_pca, run_pca_experiment
from utils import PCA_FEATURE_COLUMNS, PCA_N_COMPONENTS


def run_pipeline(competition_id, season_id, stage="all", n_neighbors=5, min_minutes=600):
    """
    Run the StatsBomb player analytics pipeline for a competition-season.
    PCA is fitted over all available competitions for the requested season.
    """

    print(
        f"Running pipeline for competition_id={competition_id}, "
        f"season_id={season_id}, " 
        f"stage={stage}"
    )

    if stage == "all":
        ingest_matches(competition_id, season_id)
        ingest_player_season_positions(competition_id, season_id)
        clean_season(competition_id, season_id)
        build_player_match_features(competition_id, season_id)
        build_player_season_features(competition_id, season_id)
        build_pca_features(season_id, min_minutes=min_minutes)
        calculate_player_percentiles(season_id)
        calculate_player_position_percentiles(season_id)
        fit_pca(season_id, n_components=PCA_N_COMPONENTS)

    elif stage == "ingest":
        ingest_matches(competition_id, season_id)
        ingest_player_season_positions(competition_id, season_id)

    elif stage == "clean":
        clean_season(competition_id, season_id)

    elif stage == "match-features":
        build_player_match_features(competition_id, season_id)

    elif stage == "season-features":
        build_player_season_features(competition_id, season_id)

    elif stage == "features":
        build_player_match_features(competition_id, season_id)
        build_player_season_features(competition_id, season_id)
    
    elif stage == "pca-fit":
        build_pca_features(season_id, min_minutes=min_minutes)
        calculate_player_percentiles(season_id)
        calculate_player_position_percentiles(season_id)
        fit_pca(season_id, n_components=PCA_N_COMPONENTS)

    elif stage == "pca-evaluate":
        mlflow.set_tracking_uri("http://127.0.0.1:5001")
        mlflow.set_experiment("statsbomb-pca")

        build_pca_features(season_id, min_minutes=min_minutes)
        calculate_player_percentiles(season_id)
        calculate_player_position_percentiles(season_id)
        standardized_features, player_scores, explained_variance, _ = fit_pca(season_id, n_components=len(PCA_FEATURE_COLUMNS), save_artifacts=False)

        for n_components in [6, 8, 10, len(PCA_FEATURE_COLUMNS)]:
            run_pca_experiment(
                season_id=season_id,
                player_scores=player_scores,
                standardized_features=standardized_features,
                explained_variance=explained_variance,
                n_components=n_components,
                n_neighbors=n_neighbors,
                min_minutes=min_minutes,
            )

    print("Pipeline complete.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the StatsBomb player analytics pipeline."
    )

    parser.add_argument(
        "--competition",
        type=int,
        required=True,
        help="StatsBomb competition ID",
    )

    parser.add_argument(
        "--season",
        type=int,
        required=True,
        help="StatsBomb season ID",
    )

    parser.add_argument(
        "--stage",
        choices=["all", "ingest", "clean", "match-features", "season-features", "features", "pca-fit", "pca-evaluate"],
        default="all",
    )

    parser.add_argument(
        "--n-neighbors",
        type=int,
        default=5,
        help="Number of neighbors used for PCA evaluation (default: 5)",
    )

    parser.add_argument(
        "--min-minutes",
        type=int,
        default=600,
        help="Minimum minutes required for PCA eligibility (default: 600)",
    )

    args = parser.parse_args()

    run_pipeline(
        competition_id=args.competition,
        season_id=args.season,
        stage=args.stage,
        n_neighbors=args.n_neighbors,
        min_minutes=args.min_minutes,
    )