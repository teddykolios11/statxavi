import { useEffect, useRef, useState } from "react";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Text,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { API_BASE_URL } from "./config.js";
import LoadingStatus from "./LoadingStatus.jsx";

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

function FeatureDifferenceTable({ title, differences }) {
  return (
    <div className="feature-difference-table">
      <h3>{title}</h3>
      <div className="profile-table-wrapper">
        <table className="profile-table">
          <thead>
            <tr>
              <th scope="col">Feature</th>
              <th scope="col" className="difference-value-heading">
                Standardized Difference
              </th>
            </tr>
          </thead>
          <tbody>
            {differences.length > 0 ? (
              differences.map(({ feature, difference }) => {
                const roundedDifference = Number(
                  Number(difference).toFixed(2),
                );
                const differenceClass =
                  roundedDifference > 0
                    ? "positive"
                    : roundedDifference < 0
                      ? "negative"
                      : "neutral";
                const formattedDifference =
                  roundedDifference === 0
                    ? "0.00"
                    : `${roundedDifference > 0 ? "+" : ""}${roundedDifference.toFixed(2)}`;

                return (
                  <tr key={feature}>
                    <th scope="row">{formatMetricName(feature)}</th>
                    <td
                      className={`difference-value difference-value-${differenceClass}`}
                    >
                      {formattedDifference}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td className="difference-empty" colSpan="2">
                  No feature differences available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
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
      <p className="feature-differences-note">
        Shows a player’s performance across six key attributes relative to
        others in their position group. Each attribute combines percentile
        rankings from related statistics.
      </p>
    </section>
  );
}

async function fetchPlayerProfile(playerName, season, signal) {
  const playerPath = `${API_BASE_URL}/players/${encodeURIComponent(playerName)}`;
  const seasonQuery = new URLSearchParams({ season });
  const [featuresResponse, percentilesResponse] = await Promise.all([
    fetch(`${playerPath}/features?${seasonQuery}`, { signal }),
    fetch(`${playerPath}/percentiles?${seasonQuery}`, { signal }),
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

const pcaPositionColors = {
  Goalkeeper: "#315bd6",
  Fullback: "#067647",
  "Center Back": "#b54708",
  "Center Midfielder": "#7f56d9",
  "Outside Midfielder": "#c11574",
  "Attacking Midfielder": "#0086c9",
  Forward: "#b42318",
};

const pcaPositionGroups = Object.keys(pcaPositionColors);
const pcaComponents = Array.from({ length: 10 }, (_, index) => `PC${index + 1}`);

function PCAMapTooltip({ active, payload, xAxis, yAxis }) {
  if (!active || !payload?.length) {
    return null;
  }

  const player = payload[0].payload;
  const teams = Array.isArray(player.teams)
    ? player.teams.join(", ")
    : player.teams || "Unknown";

  return (
    <div className="pca-tooltip">
      <strong>{player.player}</strong>
      <span>Team(s): {teams}</span>
      <span>Position: {player.position_group}</span>
      <span>
        {xAxis}: {Number(player[xAxis]).toFixed(3)}
      </span>
      <span>
        {yAxis}: {Number(player[yAxis]).toFixed(3)}
      </span>
    </div>
  );
}

function PCAMapAxisLabel({
  x,
  y,
  value,
  angle,
  fill,
  textAnchor,
  verticalAnchor,
  onHover,
  onLeave,
  isActive,
}) {
  return (
    <Text
      x={x}
      y={y}
      angle={angle}
      fill={fill}
      textAnchor={textAnchor}
      verticalAnchor={verticalAnchor}
      className="pca-axis-label"
      role="img"
      tabIndex={0}
      aria-label={`${value} axis label. Focus or hover to view top contributing features.`}
      aria-describedby={isActive ? "pca-axis-tooltip" : undefined}
      onMouseEnter={(event) => onHover(event, value)}
      onMouseLeave={onLeave}
      onFocus={(event) => onHover(event, value)}
      onBlur={onLeave}
    >
      {value}
    </Text>
  );
}

function PCAMap({
  players,
  isLoading,
  error,
  season,
  selectedPlayer,
  selectedPositionGroup,
  isLoadingPositionGroup,
  onRetry,
}) {
  const [xAxis, setXAxis] = useState("PC1");
  const [yAxis, setYAxis] = useState("PC2");
  const [samePositionOnly, setSamePositionOnly] = useState(true);
  const [topPcaFeatures, setTopPcaFeatures] = useState(null);
  const [pcaFeaturesError, setPcaFeaturesError] = useState("");
  const [isLoadingPcaFeatures, setIsLoadingPcaFeatures] = useState(false);
  const [hoveredPcaComponent, setHoveredPcaComponent] = useState("");
  const [pcaTooltipPosition, setPcaTooltipPosition] = useState({ left: 0, top: 0 });
  const pcaChartRef = useRef(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const seasonParams = new URLSearchParams({ season });
    setTopPcaFeatures(null);
    setPcaFeaturesError("");
    setIsLoadingPcaFeatures(true);

    fetch(`${API_BASE_URL}/players/top_pca_features?${seasonParams}`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load PCA feature contributions.");
        }
        return response.json();
      })
      .then((result) => {
        if (!result?.top_features || typeof result.top_features !== "object") {
          throw new Error("The PCA feature response was invalid.");
        }
        if (active) {
          setTopPcaFeatures(result.top_features);
        }
      })
      .catch((requestError) => {
        if (active) {
          setPcaFeaturesError(requestError.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingPcaFeatures(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [season]);

  function showPcaFeatureTooltip(event, component) {
    const chartBounds = pcaChartRef.current?.getBoundingClientRect();
    const labelBounds = event.currentTarget.getBoundingClientRect();
    if (!chartBounds) {
      return;
    }

    const clientX =
      event.type === "mouseenter"
        ? event.clientX
        : labelBounds.left + labelBounds.width / 2;
    const clientY =
      event.type === "mouseenter"
        ? event.clientY
        : labelBounds.top + labelBounds.height / 2;
    const pointerX = clientX - chartBounds.left;
    const pointerY = clientY - chartBounds.top;

    setPcaTooltipPosition({
      left: Math.max(8, Math.min(pointerX + 12, chartBounds.width - 280)),
      top: Math.max(8, Math.min(pointerY + 12, chartBounds.height - 160)),
    });
    setHoveredPcaComponent(component);
  }

  const hoveredFeatures = Array.isArray(topPcaFeatures?.[hoveredPcaComponent])
    ? topPcaFeatures[hoveredPcaComponent]
    : [];
  const validHoveredFeatures = hoveredFeatures.filter(
    (item) =>
      item &&
      typeof item.feature === "string" &&
      Number.isFinite(Number(item.loading)) &&
      Number.isFinite(Number(item.magnitude)),
  );
  const positiveFeatures = validHoveredFeatures
    .filter(({ loading }) => Number(loading) > 0)
    .sort((first, second) => Number(second.magnitude) - Number(first.magnitude));
  const negativeFeatures = validHoveredFeatures
    .filter(({ loading }) => Number(loading) < 0)
    .sort((first, second) => Number(second.magnitude) - Number(first.magnitude));

  const canApplyPositionFilter =
    !samePositionOnly || Boolean(selectedPositionGroup);
  const chartPlayers = canApplyPositionFilter
    ? players.filter((player) => {
        const hasCoordinates =
          Number.isFinite(Number(player[xAxis])) &&
          Number.isFinite(Number(player[yAxis]));
        const matchesPosition =
          !samePositionOnly ||
          player.position_group === selectedPositionGroup;
        return hasCoordinates && matchesPosition;
      })
    : [];

  return (
    <section className="player-content-panel pca-map-panel">
      <div className="pca-map-heading">
        <h2>Player PCA Map</h2>
        <div className="pca-map-controls">
          <label className="pca-axis-control">
            <span>X-axis</span>
            <select
              value={xAxis}
              aria-label="PCA map X-axis"
              onChange={(event) => setXAxis(event.target.value)}
            >
              {pcaComponents.map((component) => (
                <option key={component} value={component}>
                  {component}
                </option>
              ))}
            </select>
          </label>
          <label className="pca-axis-control">
            <span>Y-axis</span>
            <select
              value={yAxis}
              aria-label="PCA map Y-axis"
              onChange={(event) => setYAxis(event.target.value)}
            >
              {pcaComponents.map((component) => (
                <option key={component} value={component}>
                  {component}
                </option>
              ))}
            </select>
          </label>
          <label className="pca-position-toggle">
            <input
              type="checkbox"
              checked={samePositionOnly}
              onChange={(event) => setSamePositionOnly(event.target.checked)}
            />
            <span>Same Position Group Only</span>
          </label>
        </div>
      </div>

      <div className="pca-map-legend" aria-label="Position group legend">
        {pcaPositionGroups.map((positionGroup) => (
          <span className="pca-legend-item" key={positionGroup}>
            <span
              className="pca-legend-swatch"
              style={{ backgroundColor: pcaPositionColors[positionGroup] }}
              aria-hidden="true"
            />
            {positionGroup}
          </span>
        ))}
        <span className="pca-legend-item">
          <span className="pca-legend-selected" aria-hidden="true" />
          Selected player
        </span>
      </div>

      <LoadingStatus
        isLoading={isLoading}
        error={error}
        onRetry={onRetry}
      />
      {!isLoading && !error && players.length === 0 && (
        <p className="message">No PCA player data found for this season.</p>
      )}
      {!isLoading && !error && players.length > 0 && (
        <>
          {samePositionOnly && !selectedPositionGroup && (
            <p className="message">
              {isLoadingPositionGroup
                ? "Loading the selected player's position group..."
                : "The selected player's position group is unavailable."}
            </p>
          )}
          {canApplyPositionFilter && chartPlayers.length === 0 && (
            <p className="message">
              {samePositionOnly
                ? "No PCA players found for this position group."
                : "No players have coordinates for these axes."}
            </p>
          )}
          {chartPlayers.length > 0 && (
            <div className="pca-chart" ref={pcaChartRef}>
              {hoveredPcaComponent && (
                <div
                  id="pca-axis-tooltip"
                  className="pca-axis-tooltip"
                  role="tooltip"
                  style={pcaTooltipPosition}
                >
                  <strong>
                    {hoveredPcaComponent} — Top Contributing Features
                  </strong>
                  <span>
                    Features with the strongest influence on this principal
                    component. Signs indicate the direction of their
                    contribution.
                  </span>
                  {isLoadingPcaFeatures ? (
                    <span>Loading contributing features...</span>
                  ) : pcaFeaturesError ? (
                    <span>Contributing features are unavailable.</span>
                  ) : positiveFeatures.length + negativeFeatures.length > 0 ? (
                    <ul>
                      {positiveFeatures.map(({ feature }) => (
                        <li className="positive" key={feature}>
                          ++{feature}
                        </li>
                      ))}
                      {negativeFeatures.map(({ feature }) => (
                        <li className="negative" key={feature}>
                          --{feature}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span>No contributing features are available.</span>
                  )}
                </div>
              )}
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 12, right: 24, bottom: 12, left: 8 }}>
                  <CartesianGrid stroke="#e4e7ec" />
                  <XAxis
                    type="number"
                    dataKey={xAxis}
                    name={xAxis}
                    tick={{ fill: "#586174", fontSize: 12 }}
                    label={{
                      value: xAxis,
                      position: "insideBottom",
                      offset: -6,
                      fill: "#586174",
                      content: (labelProps) => (
                        <PCAMapAxisLabel
                          {...labelProps}
                          value={xAxis}
                          textAnchor="middle"
                          verticalAnchor="end"
                          onHover={showPcaFeatureTooltip}
                          onLeave={() => setHoveredPcaComponent("")}
                          isActive={hoveredPcaComponent === xAxis}
                        />
                      ),
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey={yAxis}
                    name={yAxis}
                    tick={{ fill: "#586174", fontSize: 12 }}
                    label={{
                      value: yAxis,
                      angle: -90,
                      position: "insideLeft",
                      fill: "#586174",
                      content: (labelProps) => (
                        <PCAMapAxisLabel
                          {...labelProps}
                          value={yAxis}
                          textAnchor="middle"
                          verticalAnchor="middle"
                          onHover={showPcaFeatureTooltip}
                          onLeave={() => setHoveredPcaComponent("")}
                          isActive={hoveredPcaComponent === yAxis}
                        />
                      ),
                    }}
                  />
                  <Tooltip
                    content={
                      <PCAMapTooltip xAxis={xAxis} yAxis={yAxis} />
                    }
                    cursor={{ strokeDasharray: "3 3" }}
                  />
                  <Scatter
                    data={chartPlayers}
                    shape={({ cx, cy, payload }) => {
                      const color =
                        pcaPositionColors[payload.position_group] ?? "#586174";
                      const isSelected = payload.player === selectedPlayer;
                      return (
                        <circle
                          cx={cx}
                          cy={cy}
                          r={isSelected ? 7 : 4}
                          fill={color}
                          stroke={isSelected ? "#172033" : "#fff"}
                          strokeWidth={isSelected ? 2 : 1}
                        />
                      );
                    }}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
      <p className="feature-differences-note">
        Explore player similarities in PCA space, where nearby players have
        similar statistical profiles. Select different components to plot and hover over each axis to see which metrics
        contribute most to that component.
      </p>
    </section>
  );
}

function App({ season, activeTab }) {
  const [query, setQuery] = useState("");
  const [players, setPlayers] = useState([]);
  const [searchError, setSearchError] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchRetryCount, setSearchRetryCount] = useState(0);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [comparisonPlayer, setComparisonPlayer] = useState("");
  const [playerInfo, setPlayerInfo] = useState(null);
  const [playerPercentiles, setPlayerPercentiles] = useState(null);
  const [playerInfoError, setPlayerInfoError] = useState("");
  const [isLoadingPlayerInfo, setIsLoadingPlayerInfo] = useState(false);
  const [similarPlayers, setSimilarPlayers] = useState([]);
  const [similarityError, setSimilarityError] = useState("");
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);
  const [similarPositionGroup, setSimilarPositionGroup] = useState("");
  const [comparisonProfiles, setComparisonProfiles] = useState(null);
  const [comparisonError, setComparisonError] = useState("");
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);
  const [featureDifferences, setFeatureDifferences] = useState(null);
  const [featureDifferencesError, setFeatureDifferencesError] = useState("");
  const [isLoadingFeatureDifferences, setIsLoadingFeatureDifferences] =
    useState(false);
  const [pcaPlayers, setPcaPlayers] = useState([]);
  const [pcaMapError, setPcaMapError] = useState("");
  const [isLoadingPcaMap, setIsLoadingPcaMap] = useState(true);
  const [pcaMapRetryCount, setPcaMapRetryCount] = useState(0);

  function selectPlayer(playerName) {
    setQuery(playerName);
    setSelectedPlayer(playerName);
  }

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const seasonParams = new URLSearchParams({ season });
    setIsLoadingPcaMap(true);
    setPcaMapError("");
    setPcaPlayers([]);

    fetch(`${API_BASE_URL}/players/pca-map?${seasonParams}`, {
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load the PCA map. Please try again.");
        }
        return response.json();
      })
      .then((results) => {
        if (!Array.isArray(results)) {
          throw new Error("The PCA map response was invalid. Please try again.");
        }
        if (active) {
          setPcaPlayers(results);
        }
      })
      .catch((requestError) => {
        if (active) {
          setPcaMapError(requestError.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingPcaMap(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [season, pcaMapRetryCount]);

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

    const searchParams = new URLSearchParams({
      query: searchTerm,
      season,
    });
    fetch(`${API_BASE_URL}/players?${searchParams}`, {
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
  }, [query, season, searchRetryCount]);

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

    const playerPath = `${API_BASE_URL}/players/${encodeURIComponent(selectedPlayer)}`;
    const seasonQuery = new URLSearchParams({ season });
    Promise.all([
      fetch(`${playerPath}/info?${seasonQuery}`, {
        signal: controller.signal,
      }),
      fetch(`${playerPath}/position_percentiles?${seasonQuery}`, {
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
  }, [selectedPlayer, season]);

  useEffect(() => {
    if (!comparisonPlayer || !selectedPlayer) {
      setComparisonProfiles(null);
      setComparisonError("");
      setIsLoadingComparison(false);
      setFeatureDifferences(null);
      setFeatureDifferencesError("");
      setIsLoadingFeatureDifferences(false);
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    setIsLoadingComparison(true);
    setComparisonError("");
    setComparisonProfiles(null);
    setIsLoadingFeatureDifferences(true);
    setFeatureDifferencesError("");
    setFeatureDifferences(null);

    Promise.all([
      fetchPlayerProfile(selectedPlayer, season, controller.signal),
      fetchPlayerProfile(comparisonPlayer, season, controller.signal),
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
  }, [comparisonPlayer, selectedPlayer, season]);

  useEffect(() => {
    if (!comparisonPlayer || !selectedPlayer) {
      return undefined;
    }

    const controller = new AbortController();
    let active = true;
    const differenceParams = new URLSearchParams({
      comparison_player: comparisonPlayer,
      season,
    });

    fetch(
      `${API_BASE_URL}/players/${encodeURIComponent(selectedPlayer)}/feature_differences?${differenceParams}`,
      { signal: controller.signal },
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            "Could not load feature differences. Please try again.",
          );
        }
        return response.json();
      })
      .then((result) => {
        if (!Array.isArray(result.differences)) {
          throw new Error(
            "Feature differences were returned in an unexpected format.",
          );
        }
        if (active) {
          setFeatureDifferences(result.differences);
        }
      })
      .catch((error) => {
        if (active) {
          setFeatureDifferencesError(error.message);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoadingFeatureDifferences(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [comparisonPlayer, selectedPlayer, season]);

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

    const similarParams = new URLSearchParams({
      season,
      n_neighbors: "5",
    });
    if (similarPositionGroup) {
      similarParams.set("position_group", similarPositionGroup);
    }
    fetch(
      `${API_BASE_URL}/players/${encodeURIComponent(selectedPlayer)}/similar?${similarParams}`,
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
  }, [selectedPlayer, season, similarPositionGroup]);

  const comparisonRows = comparisonProfiles
    ? Object.entries(comparisonProfiles[0].features).filter(
        ([metric]) =>
          Object.hasOwn(comparisonProfiles[0].percentiles, metric) &&
          Object.hasOwn(comparisonProfiles[1].features, metric) &&
          Object.hasOwn(comparisonProfiles[1].percentiles, metric),
      )
    : [];

  return comparisonPlayer ? (
    <main
      className="page comparison-page"
      id="player-search-panel"
      role="tabpanel"
      aria-labelledby="player-search-tab"
      hidden={activeTab !== "players"}
      tabIndex={0}
    >
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
        <section
          className="feature-differences-section"
          aria-labelledby="feature-differences-title"
          aria-live="polite"
        >
          <h2 id="feature-differences-title" className="visually-hidden">
            Feature similarities and differences
          </h2>
          {isLoadingFeatureDifferences && (
            <p className="message">Loading feature differences...</p>
          )}
          {featureDifferencesError && (
            <p className="message error" role="status">
              {featureDifferencesError}
            </p>
          )}
          {!isLoadingFeatureDifferences &&
            !featureDifferencesError &&
            featureDifferences && (
              <>
                <div className="feature-differences-grid">
                  <FeatureDifferenceTable
                    title="Most Similar Attributes"
                    differences={featureDifferences.slice(0, 5)}
                  />
                  <FeatureDifferenceTable
                    title="Biggest Differences"
                    differences={[...featureDifferences]
                      .slice(-5)
                      .sort(
                        (first, second) =>
                          second.absolute_difference -
                          first.absolute_difference,
                      )}
                  />
                </div>
                <p className="feature-differences-note">
                  Standardized differences are measured in standard deviations.
                  Positive values indicate higher values for {selectedPlayer};
                  negative values indicate higher values for {comparisonPlayer}.
                </p>
              </>
            )}
        </section>
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
      id="player-search-panel"
      role="tabpanel"
      aria-labelledby="player-search-tab"
      hidden={activeTab !== "players"}
      tabIndex={0}
    >
      <section className="search-panel" aria-labelledby="page-title">
        <h1 id="page-title">Player Search</h1>
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

        {(isSearching ||
          searchError ||
          (!selectedPlayer && (isLoadingPcaMap || pcaMapError))) && (
          <LoadingStatus
            key={isSearching ? "search" : "pca"}
            isLoading={
              isSearching || (!selectedPlayer && isLoadingPcaMap)
            }
            error={isSearching ? "" : searchError || pcaMapError}
            onRetry={() => {
              if (searchError) {
                setSearchRetryCount((count) => count + 1);
              } else {
                setPcaMapRetryCount((count) => count + 1);
              }
            }}
          />
        )}
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
            <div className="similarity-section-heading">
              <h2>Statistically similar to {selectedPlayer}</h2>
              <label className="similarity-position-filter">
                <span className="visually-hidden">
                  Filter similar players by position group
                </span>
                <select
                  className="similarity-position-select"
                  value={similarPositionGroup}
                  aria-label="Filter similar players by position group"
                  onChange={(event) =>
                    setSimilarPositionGroup(event.target.value)
                  }
                >
                  <option value="">All Positions</option>
                  <option value="Goalkeeper">Goalkeeper</option>
                  <option value="Fullback">Fullback</option>
                  <option value="Center Back">Center Back</option>
                  <option value="Center Midfielder">Center Midfielder</option>
                  <option value="Outside Midfielder">Outside Midfielder</option>
                  <option value="Attacking Midfielder">
                    Attacking Midfielder
                  </option>
                  <option value="Forward">Forward</option>
                </select>
              </label>
            </div>
            {isLoadingSimilar && <p className="message">Loading players...</p>}
            {similarityError && (
              <p className="message error">{similarityError}</p>
            )}
            {!isLoadingSimilar &&
              !similarityError &&
              similarPlayers.length === 0 && (
                <p className="message">
                  {similarPositionGroup
                    ? "No similar players found for this position group."
                    : "No similar players found."}
                </p>
              )}
            {similarPlayers.length > 0 && (
              <ul className="similar-player-list">
                {similarPlayers.map((player) => {
                  const score = Number(player.similarity_score);
                  const scoreColor =
                    score >= 75
                      ? "high"
                      : score >= 65
                        ? "medium"
                        : "low";

                  return (
                    <li className="similar-player-card" key={player.player}>
                      <div className="similar-player-heading">
                        <button
                          type="button"
                          className="player-name similar-player-name"
                          onClick={() => selectPlayer(player.player)}
                        >
                          {player.player}
                        </button>
                        <span
                          className={`similarity-score similarity-score-${scoreColor}`}
                          aria-label={`Similarity: ${Math.round(score)}%`}
                        >
                          <span className="similarity-score-label">
                            Similarity
                          </span>
                          <span>{Math.round(score)}%</span>
                        </span>
                      </div>
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
                  );
                })}
              </ul>
            )}
            <p className="feature-differences-note">
              Displays the five most statistically similar players based on our
              PCA model. Similarity scores reflect how closely their
              statistical profiles align. Click ‘Compare Profiles’ for a
              detailed breakdown.
            </p>
          </section>
          <PCAMap
            players={pcaPlayers}
            isLoading={isLoadingPcaMap}
            error={pcaMapError}
            season={season}
            selectedPlayer={selectedPlayer}
            selectedPositionGroup={playerInfo?.position_group}
            isLoadingPositionGroup={isLoadingPlayerInfo}
            onRetry={() => setPcaMapRetryCount((count) => count + 1)}
          />
        </div>
      )}
    </main>
  );
}

export default App;
