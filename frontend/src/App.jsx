import { useEffect, useState } from "react";

const percentileColorByMetric = {
  goals: "blue",
  xG: "blue",
  shots: "blue",
  xA: "green",
  shot_assists: "green",
  progressive_passes: "green",
  passes_completed: "green",
  pass_completion: "green",
  dribbles_attempted: "yellow",
  dribbles_completed: "yellow",
  carries: "yellow",
  progressive_carries: "yellow",
  ball_recoveries_won: "red",
  interceptions_won: "red",
  duels: "red",
  tackles_won: "red",
  blocks: "red",
  clearances: "red",
  pressures: "red",
  fouls: "red",
  poss_won_final_third: "red",
};

const positionAttributes = {
  Goalkeeper: [
    {
      name: "Defensive Engagement",
      features: ["tackles_won_per90", "duels_per90", "pressures_per90"],
    },
    {
      name: "Interceptions & Recovery",
      features: ["interceptions_won_per90", "ball_recoveries_won_per90"],
    },
    {
      name: "Defensive Clearances",
      features: ["clearances_per90", "blocks_per90"],
    },
    { name: "Passing Volume", features: ["passes_completed_per90"] },
    {
      name: "Passing Progression",
      features: ["progressive_passes_per90", "progressive_carries_per90"],
    },
    { name: "Passing Security", features: ["pass_completion_pct"] },
  ],
  "Center Back": [
    {
      name: "Defensive Engagement",
      features: ["tackles_won_per90", "duels_per90", "pressures_per90"],
    },
    {
      name: "Ball Recovery",
      features: ["interceptions_won_per90", "ball_recoveries_won_per90"],
    },
    {
      name: "Defensive Clearances",
      features: ["clearances_per90", "blocks_per90"],
    },
    { name: "Passing Volume", features: ["passes_completed_per90"] },
    {
      name: "Passing Progression",
      features: ["progressive_passes_per90", "progressive_carries_per90"],
    },
    { name: "Passing Security", features: ["pass_completion_pct"] },
  ],
  Fullback: [
    {
      name: "Defensive Engagement",
      features: ["tackles_won_per90", "duels_per90", "pressures_per90"],
    },
    {
      name: "Ball Recovery",
      features: ["interceptions_won_per90", "ball_recoveries_won_per90"],
    },
    { name: "Passing Progression", features: ["progressive_passes_per90"] },
    {
      name: "Passing Volume & Security",
      features: ["passes_completed_per90", "pass_completion_pct"],
    },
    {
      name: "Ball Carrying",
      features: ["carries_per90", "progressive_carries_per90"],
    },
    {
      name: "Chance Creation",
      features: ["xA_per90", "shot_assists_per90"],
    },
  ],
  "Center Midfielder": [
    {
      name: "Defensive Engagement",
      features: ["tackles_won_per90", "duels_per90", "pressures_per90"],
    },
    {
      name: "Ball Recovery",
      features: ["interceptions_won_per90", "ball_recoveries_won_per90"],
    },
    { name: "Passing Progression", features: ["progressive_passes_per90"] },
    {
      name: "Passing Volume & Security",
      features: ["passes_completed_per90", "pass_completion_pct"],
    },
    {
      name: "Ball Carrying",
      features: ["carries_per90", "progressive_carries_per90"],
    },
    {
      name: "Chance Creation",
      features: ["xA_per90", "shot_assists_per90"],
    },
  ],
  "Attacking Midfielder": [
    { name: "Passing Progression", features: ["progressive_passes_per90"] },
    {
      name: "Passing Volume & Security",
      features: ["passes_completed_per90", "pass_completion_pct"],
    },
    {
      name: "Ball Carrying",
      features: ["carries_per90", "progressive_carries_per90"],
    },
    {
      name: "Dribbling",
      features: ["dribbles_attempted_per90", "dribbles_completed_per90"],
    },
    {
      name: "Chance Creation",
      features: ["xA_per90", "shot_assists_per90"],
    },
    {
      name: "Goal Threat",
      features: ["xG_per90", "shots_per90", "goals_per90"],
    },
  ],
  "Outside Midfielder": [
    {
      name: "Defensive Work Rate",
      features: [
        "pressures_per90",
        "tackles_won_per90",
        "poss_won_final_third_per90",
      ],
    },
    { name: "Passing Progression", features: ["progressive_passes_per90"] },
    {
      name: "Ball Carrying",
      features: ["carries_per90", "progressive_carries_per90"],
    },
    {
      name: "Dribbling",
      features: ["dribbles_attempted_per90", "dribbles_completed_per90"],
    },
    {
      name: "Chance Creation",
      features: ["xA_per90", "shot_assists_per90"],
    },
    {
      name: "Goal Threat",
      features: ["xG_per90", "shots_per90", "goals_per90"],
    },
  ],
  Forward: [
    {
      name: "Defensive Work Rate",
      features: [
        "pressures_per90",
        "tackles_won_per90",
        "poss_won_final_third_per90",
      ],
    },
    {
      name: "Link-Up Play",
      features: ["passes_completed_per90", "pass_completion_pct"],
    },
    {
      name: "Dribbling",
      features: ["dribbles_attempted_per90", "dribbles_completed_per90"],
    },
    {
      name: "Chance Creation",
      features: ["xA_per90", "shot_assists_per90"],
    },
    { name: "Goal Threat", features: ["xG_per90", "shots_per90"] },
    { name: "Goalscoring Output", features: ["goals_per90"] },
  ],
};

function formatMetricName(metric) {
  const label = metric
    .replace(/_per90$/, " / 90")
    .replace(/_pct$/, " %")
    .replaceAll("_", " ");

  return label
    .replace(/\b\w/g, (character) => character.toUpperCase())
    .replace(/\bXG\b/g, "xG")
    .replace(/\bXA\b/g, "xA");
}

function PercentileBar({ metric, percentile }) {
  const boundedPercentile = Math.min(100, Math.max(0, percentile));
  const color = percentileColorByMetric[
    metric.replace(/_(per90|pct)$/, "")
  ] ?? "blue";

  return (
    <div className="percentile-value">
      <span>{percentile.toFixed(1)}</span>
      <span
        className="percentile-track"
        role="progressbar"
        aria-label={`${formatMetricName(metric)} percentile`}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={boundedPercentile}
      >
        <span
          className={`percentile-fill percentile-fill--${color}`}
          style={{ width: `${boundedPercentile}%` }}
        />
      </span>
    </div>
  );
}

function HexagonProfile({ positionGroup, percentiles }) {
  const [hoveredAttribute, setHoveredAttribute] = useState(null);
  const [focusedAttribute, setFocusedAttribute] = useState(null);
  const center = 210;
  const verticalCenter = 160;
  const radius = 78;
  const labelRadius = 112;
  const axes = Array.from({ length: 6 }, (_, index) => {
    const angle = ((index * 60 - 90) * Math.PI) / 180;
    return {
      vertex: [
        center + radius * Math.cos(angle),
        verticalCenter + radius * Math.sin(angle),
      ],
      label: [
        center + labelRadius * Math.cos(angle),
        verticalCenter + labelRadius * Math.sin(angle),
      ],
    };
  });
  const pointString = (scale) =>
    axes
      .map(({ vertex: [x, y] }) =>
        `${center + (x - center) * scale},${verticalCenter + (y - verticalCenter) * scale}`,
      )
      .join(" ");
  const attributes = (positionAttributes[positionGroup] ?? []).map(
    (attribute, index) => {
      const featureValues = attribute.features.map((feature) => ({
        feature,
        value: Number(percentiles[feature]),
      }));

      return {
        ...attribute,
        index,
        featureValues,
        score:
          featureValues.reduce((total, item) => total + item.value, 0) /
          featureValues.length,
      };
    },
  );
  const activeAttribute =
    attributes[hoveredAttribute ?? focusedAttribute] ?? null;

  return (
    <section className="player-content-panel hexagon-panel">
      <h2>Statistical Profile</h2>
      <div className="hexagon-visual">
        <div className="hexagon-chart">
          <svg
            viewBox="0 0 420 320"
            role="group"
            aria-label={`${positionGroup ?? "Player"} six-attribute statistical profile`}
          >
            {[0.25, 0.5, 0.75, 1].map((scale) => (
              <polygon
                key={scale}
                points={pointString(scale)}
                className="hexagon-gridline"
              />
            ))}
            {axes.map(({ vertex: [x, y] }, index) => (
              <line
                key={index}
                x1={center}
                y1={verticalCenter}
                x2={x}
                y2={y}
                className="hexagon-axis"
              />
            ))}
            {attributes.length === 6 && (
              <polygon
                points={attributes
                  .map(({ index, score }) => {
                    const [x, y] = axes[index].vertex;
                    const scale = Math.max(0, Math.min(100, score)) / 100;
                    return `${center + (x - center) * scale},${verticalCenter + (y - verticalCenter) * scale}`;
                  })
                  .join(" ")}
                className="hexagon-profile-polygon"
              />
            )}
            {attributes.map(({ name, index, score }, attributeIndex) => {
              const [x, y] = axes[index].vertex;
              const scale = Math.max(0, Math.min(100, score)) / 100;
              const pointX = center + (x - center) * scale;
              const pointY = verticalCenter + (y - verticalCenter) * scale;
              const [labelX, labelY] = axes[index].label;
              const anchor =
                labelX < center - 10
                  ? "end"
                  : labelX > center + 10
                    ? "start"
                    : "middle";

              return (
                <g key={name}>
                  <text
                    x={labelX}
                    y={labelY}
                    textAnchor={anchor}
                    className="hexagon-label"
                  >
                    {name}
                  </text>
                  <text
                    x={labelX}
                    y={labelY + 15}
                    textAnchor={anchor}
                    className="hexagon-score"
                  >
                    {Math.round(score)}
                  </text>
                  <circle
                    cx={pointX}
                    cy={pointY}
                    r="5"
                    className={`hexagon-point${hoveredAttribute === attributeIndex ? " is-active" : ""}`}
                  />
                  <circle
                    cx={pointX}
                    cy={pointY}
                    r="13"
                    className="hexagon-point-target"
                    role="button"
                    tabIndex="0"
                    aria-label={`${name}: ${Math.round(score)}`}
                    onMouseEnter={() => setHoveredAttribute(attributeIndex)}
                    onMouseLeave={() => setHoveredAttribute(null)}
                    onFocus={() => setFocusedAttribute(attributeIndex)}
                    onBlur={() => setFocusedAttribute(null)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        setFocusedAttribute(attributeIndex);
                      }
                    }}
                    onClick={() =>
                      setFocusedAttribute((current) =>
                        current === attributeIndex ? null : attributeIndex,
                      )
                    }
                  />
                </g>
              );
            })}
          </svg>
          {activeAttribute && (
            <div className="hexagon-tooltip" role="status">
              <strong>
                {activeAttribute.name} — {Math.round(activeAttribute.score)}
              </strong>
              <div className="hexagon-tooltip-columns">
                <span>Feature</span>
                <span>Percentile</span>
              </div>
              <dl>
                {activeAttribute.featureValues.map(({ feature, value }) => (
                  <div key={feature}>
                    <dt>{formatMetricName(feature)}</dt>
                    <dd>{Math.round(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

async function fetchPlayerProfile(playerName, signal) {
  const playerPath = `/players/${encodeURIComponent(playerName)}`;
  const [featuresResponse, percentilesResponse] = await Promise.all([
    fetch(`${playerPath}/features`, { signal }),
    fetch(`${playerPath}/percentiles`, { signal }),
  ]);

  if (!featuresResponse.ok || !percentilesResponse.ok) {
    throw new Error(
      "Could not load the player's statistical profile. Please try again.",
    );
  }

  const [features, percentiles] = await Promise.all([
    featuresResponse.json(),
    percentilesResponse.json(),
  ]);

  return {
    features: features.features,
    percentiles: percentiles.percentiles,
  };
}

function App() {
  const [query, setQuery] = useState("");
  const [players, setPlayers] = useState([]);
  const [searchError, setSearchError] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [comparisonPlayer, setComparisonPlayer] = useState("");
  const [playerInfo, setPlayerInfo] = useState(null);
  const [playerPercentiles, setPlayerPercentiles] = useState(null);
  const [playerInfoError, setPlayerInfoError] = useState("");
  const [isLoadingPlayerInfo, setIsLoadingPlayerInfo] = useState(false);
  const [similarPlayers, setSimilarPlayers] = useState([]);
  const [similarityError, setSimilarityError] = useState("");
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);
  const [comparisonProfiles, setComparisonProfiles] = useState(null);
  const [comparisonError, setComparisonError] = useState("");
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);

  function selectPlayer(playerName) {
    setQuery(playerName);
    setSelectedPlayer(playerName);
  }

  useEffect(() => {
    const searchTerm = query.trim();
    if (!searchTerm) {
      setPlayers([]);
      setSearchError("");
      setHasSearched(false);
      setIsSearching(false);
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setIsSearching(true);
    setSearchError("");
    setPlayers([]);
    setHasSearched(false);

    fetch(`/players?query=${encodeURIComponent(searchTerm)}`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Player search failed. Please try again.");
        }
        return response.json();
      })
      .then((results) => {
        if (active) {
          setPlayers(results);
          setHasSearched(true);
        }
      })
      .catch((searchError) => {
        if (active) {
          setSearchError(searchError.message);
          setPlayers([]);
        }
      })
      .finally(() => {
        if (active) {
          setIsSearching(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [query]);

  useEffect(() => {
    if (!selectedPlayer) {
      setPlayerInfo(null);
      setPlayerPercentiles(null);
      setPlayerInfoError("");
      setIsLoadingPlayerInfo(false);
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setIsLoadingPlayerInfo(true);
    setPlayerInfoError("");
    setPlayerInfo(null);
    setPlayerPercentiles(null);

    const playerPath = `/players/${encodeURIComponent(selectedPlayer)}`;
    Promise.all([
      fetch(`${playerPath}/info`, { signal: controller.signal }),
      fetch(`${playerPath}/position_percentiles`, {
        signal: controller.signal,
      }),
    ])
      .then(async ([infoResponse, percentileResponse]) => {
        if (!infoResponse.ok || !percentileResponse.ok) {
          throw new Error("Could not load player information. Please try again.");
        }
        const [info, percentiles] = await Promise.all([
          infoResponse.json(),
          percentileResponse.json(),
        ]);
        return { info, percentiles };
      })
      .then(({ info, percentiles }) => {
        if (active) {
          setPlayerInfo(info);
          setPlayerPercentiles(percentiles.percentiles);
        }
      })
      .catch((error) => {
        if (active) {
          setPlayerInfoError(error.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingPlayerInfo(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [selectedPlayer]);

  useEffect(() => {
    if (!comparisonPlayer || !selectedPlayer) {
      setComparisonProfiles(null);
      setComparisonError("");
      setIsLoadingComparison(false);
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setIsLoadingComparison(true);
    setComparisonError("");
    setComparisonProfiles(null);

    Promise.all([
      fetchPlayerProfile(selectedPlayer, controller.signal),
      fetchPlayerProfile(comparisonPlayer, controller.signal),
    ])
      .then(([originalProfile, comparisonProfile]) => {
        if (active) {
          setComparisonProfiles([originalProfile, comparisonProfile]);
        }
      })
      .catch((error) => {
        if (active) {
          setComparisonError(error.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingComparison(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [comparisonPlayer, selectedPlayer]);

  useEffect(() => {
    if (!selectedPlayer) {
      setSimilarPlayers([]);
      setSimilarityError("");
      setIsLoadingSimilar(false);
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setIsLoadingSimilar(true);
    setSimilarityError("");
    setSimilarPlayers([]);

    fetch(
      `/players/${encodeURIComponent(selectedPlayer)}/similar?n_neighbors=5`,
      { signal: controller.signal },
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load similar players. Please try again.");
        }
        return response.json();
      })
      .then((results) => {
        if (active) {
          setSimilarPlayers(results);
        }
      })
      .catch((error) => {
        if (active) {
          setSimilarityError(error.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingSimilar(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [selectedPlayer]);

  const comparisonRows = comparisonProfiles
    ? Object.entries(comparisonProfiles[0].features).filter(
        ([metric]) =>
          Object.hasOwn(comparisonProfiles[0].percentiles, metric) &&
          Object.hasOwn(comparisonProfiles[1].features, metric) &&
          Object.hasOwn(comparisonProfiles[1].percentiles, metric),
      )
    : [];

  return comparisonPlayer ? (
    <main className="page comparison-page">
      <section className="search-panel" aria-labelledby="comparison-title">
        <button
          type="button"
          className="back-link"
          onClick={() => setComparisonPlayer("")}
        >
          Back to Player Profile
        </button>
        <h1 id="comparison-title">Compare Profiles</h1>
        {isLoadingComparison && (
          <p className="message">Loading player profiles...</p>
        )}
        {comparisonError && (
          <p className="message error">{comparisonError}</p>
        )}
        {comparisonProfiles && (
          <div className="profile-table-wrapper">
            <table className="profile-table comparison-table">
              <thead>
                <tr>
                  <th scope="col" rowSpan="2">Metric</th>
                  <th scope="colgroup" colSpan="2" className="player-a-columns">
                    {selectedPlayer}
                  </th>
                  <th scope="colgroup" colSpan="2" className="player-b-columns">
                    {comparisonPlayer}
                  </th>
                </tr>
                <tr>
                  <th scope="col" className="player-a-columns">Actual Value</th>
                  <th scope="col">Percentile</th>
                  <th scope="col" className="player-b-columns">Actual Value</th>
                  <th scope="col">Percentile</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map(([metric, originalValue]) => {
                  const originalPercentile = Number(
                    comparisonProfiles[0].percentiles[metric],
                  );
                  const otherPercentile = Number(
                    comparisonProfiles[1].percentiles[metric],
                  );

                  return (
                    <tr key={metric}>
                      <th scope="row">{formatMetricName(metric)}</th>
                      <td className="player-a-columns">
                        {Number(originalValue).toFixed(2)}
                      </td>
                      <td>
                        <PercentileBar
                          metric={metric}
                          percentile={originalPercentile}
                        />
                      </td>
                      <td className="player-b-columns">
                        {Number(comparisonProfiles[1].features[metric]).toFixed(2)}
                      </td>
                      <td>
                        <PercentileBar
                          metric={metric}
                          percentile={otherPercentile}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  ) : (
    <main
      className={`page player-page${selectedPlayer ? " has-selected-player" : ""}`}
    >
      <section className="search-panel" aria-labelledby="page-title">
        <h1 id="page-title">Player search</h1>
        <div className="search-form">
          <label className="visually-hidden" htmlFor="player-query">
            Search players
          </label>
          <input
            id="player-query"
            type="search"
            placeholder="Enter a player name"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setSelectedPlayer("");
            }}
          />
        </div>

        {searchError && <p className="message error">{searchError}</p>}
        {!searchError && players.length === 0 && !isSearching && hasSearched && (
          <p className="message">No players found.</p>
        )}
        {players.length > 0 && !selectedPlayer && (
          <ul className="player-list player-options" aria-label="Player matches">
            {players.map((player) => (
              <li key={player.player}>
                <button
                  type="button"
                  onClick={() => selectPlayer(player.player)}
                >
                  <span className="player-name">{player.player}</span>
                  <span className="player-details">
                    {player.primary_position}
                    {player.teams?.length > 0 &&
                      ` · ${player.teams.join(", ")}`}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selectedPlayer && (
        <div className="player-content">
          <div className="player-profile-layout">
            <section
              className="player-content-panel player-info-panel"
              aria-live="polite"
            >
              <h2>Player Information</h2>
              {isLoadingPlayerInfo && (
                <p className="message">Loading player information...</p>
              )}
              {playerInfoError && (
                <p className="message error">{playerInfoError}</p>
              )}
              {playerInfo && (
                <dl className="player-info-grid">
                  <div>
                    <dt>Player Name</dt>
                    <dd>{playerInfo.player}</dd>
                  </div>
                  <div>
                    <dt>Competition</dt>
                    <dd>{playerInfo.competition}</dd>
                  </div>
                  <div>
                    <dt>Team(s)</dt>
                    <dd>
                      {Array.isArray(playerInfo.team)
                        ? playerInfo.team.join(", ")
                        : playerInfo.team}
                    </dd>
                  </div>
                  <div>
                    <dt>Appearances</dt>
                    <dd>{playerInfo.matches_played}</dd>
                  </div>
                  <div>
                    <dt>Starts</dt>
                    <dd>{playerInfo.starts}</dd>
                  </div>
                  <div>
                    <dt>Minutes Played</dt>
                    <dd>
                      {Number(playerInfo.minutes_played).toLocaleString()}
                    </dd>
                  </div>
                  <div>
                    <dt>Primary Position</dt>
                    <dd>{playerInfo.primary_position}</dd>
                  </div>
                  <div>
                    <dt>Position Group</dt>
                    <dd>{playerInfo.position_group}</dd>
                  </div>
                </dl>
              )}
            </section>
            <HexagonProfile
              positionGroup={playerInfo?.position_group}
              percentiles={playerPercentiles ?? {}}
            />
          </div>

          <section className="player-content-panel similarity-results" aria-live="polite">
            <h2>Players similar to {selectedPlayer}</h2>
            {isLoadingSimilar && <p className="message">Loading players...</p>}
            {similarityError && (
              <p className="message error">{similarityError}</p>
            )}
            {!isLoadingSimilar &&
              !similarityError &&
              similarPlayers.length === 0 && (
                <p className="message">No similar players found.</p>
              )}
            {similarPlayers.length > 0 && (
              <ul className="similar-player-list">
                {similarPlayers.map((player) => (
                  <li className="similar-player-card" key={player.player}>
                    <button
                      type="button"
                      className="player-name similar-player-name"
                      onClick={() => selectPlayer(player.player)}
                    >
                      {player.player}
                    </button>
                    <span className="player-details">
                      {player.primary_position}
                    </span>
                    {player.teams?.length > 0 && (
                      <span className="player-team">
                        {player.teams.join(", ")}
                      </span>
                    )}
                    <button
                      type="button"
                      className="compare-button"
                      onClick={() => setComparisonPlayer(player.player)}
                    >
                      Compare Profiles
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </main>
  );
}

export default App;
