const methodologyCards = [
  {
    title: "Data Source",
    question: "Where does the data come from?",
    description:
      "StatXavi uses publicly available StatsBomb event data, aggregated into season-level player profiles. Only players with at least 600 minutes played for club competitions or 180 minutes for international competitions are included in similarity analysis.",
    icon: (
      <>
        <ellipse cx="12" cy="5" rx="8" ry="3" />
        <path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
        <path d="M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7" />
      </>
    ),
  },
  {
    title: "Player Profiles",
    question: "How are player attributes calculated?",
    description:
      "Player performance is measured across passing, ball progression, attacking output, and defensive activity. Statistics are normalized per 90 minutes, while player profile percentiles are calculated relative to players in the same position group.",
    icon: (
      <>
        <path d="M3 3v18h18" />
        <path d="m7 14 4-4 4 3 6-7" />
      </>
    ),
  },
  {
    title: "Player Similarity",
    question: "How are similar players identified?",
    description:
      "Player statistics are standardized and transformed using Principal Component Analysis (PCA). Similarity is calculated using the distance between players in this reduced statistical space. Smaller distances indicate more similar statistical profiles. Users can optionally filter similarity results by position group.",
    icon: (
      <>
        <circle cx="6" cy="6" r="2.5" />
        <circle cx="18" cy="7" r="2.5" />
        <circle cx="12" cy="18" r="2.5" />
        <path d="m8 7 7.5-.2M7.5 8l3.2 7.5m5.8-6.4-3.2 6.4" />
      </>
    ),
  },
  {
    title: "Understanding the PCA Map",
    question: "What does the visualization show?",
    description:
      "Each point represents a player positioned according to their PCA scores. Nearby players generally share similar statistical characteristics along the displayed components. Hovering over a PCA axis label reveals the underlying features contributing most strongly to that component.",
    icon: (
      <>
        <path d="M3 3v18h18" />
        <circle cx="8" cy="15" r="1.5" />
        <circle cx="12" cy="10" r="1.5" />
        <circle cx="17" cy="7" r="1.5" />
      </>
    ),
  },
];

function MethodologyIcon({ children }) {
  return (
    <svg
      className="methodology-card-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

function Methodology({ activeTab }) {
  return (
    <main
      className="page methodology-page"
      id="methodology-panel"
      role="tabpanel"
      aria-labelledby="methodology-tab"
      hidden={activeTab !== "methodology"}
      tabIndex={0}
    >
      <header className="methodology-intro">
        <h1 id="methodology-title">How StatXavi works</h1>
        <p>
          A quick guide to the data and methods behind player profiles,
          similarity, and the PCA map.
        </p>
      </header>

      <div className="methodology-grid">
        {methodologyCards.map((card) => (
          <article className="methodology-card" key={card.title}>
            <div className="methodology-card-heading">
              <MethodologyIcon>{card.icon}</MethodologyIcon>
              <h2>{card.title}</h2>
            </div>
            <p className="methodology-question">{card.question}</p>
            <p className="methodology-description">{card.description}</p>
          </article>
        ))}
      </div>

      <aside className="methodology-note" aria-labelledby="interpretation-title">
        <svg
          className="methodology-note-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          focusable="false"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 11v5m0-8h.01" />
        </svg>
        <div>
          <h2 id="interpretation-title">A Note on Interpretation</h2>
          <p>
            StatXavi measures statistical similarity, not overall player
            quality. Results depend on available data, playing time, and
            tactical roles. Players appearing close together on the PCA map are
            not necessarily the closest matches in the full similarity model.
          </p>
        </div>
      </aside>
    </main>
  );
}

export default Methodology;
