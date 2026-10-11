# StatXavi ⚽

**Explore football player profiles and discover similar players using event data and principal component analysis (PCA).**

StatXavi is an end-to-end soccer analytics project that turns StatsBomb event data into interpretable player statistics, lower-dimensional player representations, and interactive similarity recommendations. It combines a Python data pipeline, scikit-learn modeling, a FastAPI backend, and a React frontend.

> **Project status:** Active development. Current analysis focuses on the 2015/16 season and available StatsBomb open-data matches from the Premier League, La Liga, Serie A, and Ligue 1. Coverage is limited to matches present in the open dataset; results should not be interpreted as complete league-season coverage without verification.

<!-- TODO: Add a screenshot or GIF of the app here. -->
<!-- ![StatXavi screenshot](docs/assets/statxavi-demo.png) -->

## Features

- **Player search:** Find players and inspect their teams, appearances, minutes, and primary position.
- **Similar-player discovery:** Retrieve nearest neighbors in PCA-based player-feature space.
- **Player profiles:** Explore position-group-relative percentile attributes in a hexagon visualization.
- **Side-by-side statistics:** Compare underlying player metrics independently of the hexagon's position-specific percentile view.
- **Reproducible analytics pipeline:** Aggregate match events into player-match and player-season features.
- **Model evaluation:** Track PCA variance explained, neighborhood preservation, trustworthiness, and position-group consistency with MLflow.

## How it works

```text
StatsBomb open event data
          |
          v
Event ingestion and cleaning
          |
          v
Player-match features
          |
          v
Player-season aggregates + positions
          |
          v
Per-90 rates and derived metrics
          |
          v
StandardScaler -> PCA (10 components)
          |
          v
Player embeddings -> nearest neighbors
          |
          v
FastAPI endpoints -> React / Vite UI
```

The model uses a mix of attacking, passing, carrying, and defensive activity measures. Examples include xG/90, xA/90, progressive passes/90, dribbles/90, pressures/90, interceptions/90, and pass completion percentage. Players must have **at least 600 minutes** in the modeled sample.

### Similarity methodology

1. Aggregate event-derived features for each player across available matches in a season.
2. Convert volume metrics to per-90 rates and retain relevant percentage metrics.
3. Standardize features using `StandardScaler`.
4. Fit PCA across players from the included competitions; the current configuration retains **10 principal components**.
5. Find nearby players in the resulting component space.

PCA is used for **player similarity**, not position classification. Position-group consistency is monitored as a diagnostic rather than optimized as the primary objective.

> **Interpretation note:** Similarity means statistical proximity under the selected features and distance metric; it does not establish identical tactical roles, player quality, or scouting suitability. Exact neighbor-ranking details should be verified against the current implementation.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Data processing | Python, pandas, Parquet, StatsBomb open data |
| Modeling | scikit-learn, PCA, nearest-neighbor similarity |
| Experiment tracking | MLflow |
| API | FastAPI, Uvicorn |
| Frontend | React, Vite |

## Repository layout

The following is a **suggested layout**; adapt paths to the actual repository before publishing.

```text
statxavi/
├── data/
│   ├── processed/<competition>/<season>/
│   └── model/<season>/pca_features.parquet
├── models/
│   └── pca/<season>/
│       ├── player_scores.parquet
│       ├── explained_variance.parquet
│       ├── loadings.parquet
│       ├── scaler.pkl
│       ├── pca.pkl
│       └── metadata.json
├── src/                    # Data processing / model code
├── backend/                # FastAPI app (confirm actual path)
├── frontend/               # React / Vite app (confirm actual path)
├── docs/
└── README.md
```

Large datasets, generated models, local environments, and secrets should be excluded from Git unless intentionally published under suitable licenses.

## Getting started

> **Before publishing:** Replace the placeholders below with verified paths, commands, environment variables, and dependency files from the repository. Do not assume these commands work unchanged.

### Prerequisites

- Python environment with project dependencies installed
- Node.js and npm for the React/Vite frontend
- Access to the event data or locally generated Parquet/model artifacts

### Run the API

```bash
# From the repository root, after installing Python dependencies:
# TODO: replace `backend.main:app` with the actual FastAPI import path
uvicorn backend.main:app --reload
```

### Run the frontend

```bash
# TODO: verify frontend directory and scripts
cd frontend
npm install
npm run dev
```

### Build the data and model artifacts

The project includes stages for event ingestion, player-match aggregation, player-season aggregation, position derivation, feature preparation, and PCA fitting. **TODO:** Document the exact scripts/CLI commands and their execution order in [`docs/data-pipeline.md`](docs/data-pipeline.md) and [`docs/modeling.md`](docs/modeling.md).

## API overview

| Endpoint | Purpose |
| --- | --- |
| `GET /players?query=...` | Search players |
| `GET /players/{player_name}/info` | Player information |
| `GET /players/{player_name}/similar` | Similar players; supports `n_neighbors` |
| `GET /players/{player_name}/percentiles` | Overall percentile data for statistical comparisons |
| `GET /players/{player_name}/position_percentiles` | Position-group-relative percentiles for the hexagon profile |

Once the backend is running, visit its `/docs` route for interactive OpenAPI documentation. Response shapes and defaults should be verified against the source.

## Model evaluation

The selected 10-component configuration explained approximately **92.2%** of standardized feature variance in a development experiment. Other recorded diagnostics included trustworthiness (~0.997), top-k neighbor preservation (~0.639), and position-group consistency (~0.765); metric definitions, neighborhood sizes, and experiment provenance should be documented before treating these as comparable benchmark results.

Evaluation emphasizes whether nearby players in the compressed space remain meaningful neighbors, rather than maximizing explained variance alone. See [`docs/modeling.md`](docs/modeling.md) for planned methodological details.

## Limitations and roadmap

- **Coverage:** Open-data availability varies by competition and season.
- **Sample selection:** The 600-minute threshold excludes lower-minute players.
- **Context:** Per-90 event statistics do not fully control for team style, opposition, possession, or tactical responsibilities.
- **Model drift:** Adding leagues, seasons, or features requires refitting the scaler and PCA, then reevaluating neighbors.
- **Planned improvements:** Broader validated coverage, richer similarity explanations, stronger evaluation, tests, and deployment documentation.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — system components and data flow
- [`docs/data-pipeline.md`](docs/data-pipeline.md) — ingestion, cleaning, aggregations, and artifacts
- [`docs/feature-engineering.md`](docs/feature-engineering.md) — metric definitions and position derivation
- [`docs/modeling.md`](docs/modeling.md) — preprocessing, PCA, similarity, and evaluation
- [`docs/api.md`](docs/api.md) — endpoint contracts and example responses
- [`docs/development.md`](docs/development.md) — local setup, testing, and troubleshooting
- [`docs/data-sources.md`](docs/data-sources.md) — dataset scope, licensing, and attribution

## Data attribution

This project uses **StatsBomb open data**. Credit StatsBomb and comply with the terms and attribution requirements applicable to the dataset. Before publishing, add a direct link to the exact data source, confirm its license/usage terms, and distinguish original StatsBomb data from StatXavi's derived features.

## Author

Developed by [Theodore Kolios](https://github.com/teddykolios11).

<!-- TODO: Add a verified license (LICENSE file) and deployment URL if applicable. -->
