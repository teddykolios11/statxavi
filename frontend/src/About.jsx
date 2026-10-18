const competitions = [
  { season: "2015/16", competitions: "Premier League, La Liga, Serie A, Ligue 1" },
  { season: "2018", competitions: "FIFA World Cup" },
  { season: "2020", competitions: "UEFA European Championship" },
  { season: "2022", competitions: "FIFA World Cup" },
  { season: "2024", competitions: "UEFA European Championship" },
];

function About({ activeTab }) {
  return (
    <main
      className="page methodology-page about-page"
      id="about-panel"
      role="tabpanel"
      aria-labelledby="about-tab"
      hidden={activeTab !== "about"}
      tabIndex={0}
    >
      <header className="methodology-intro">
        <h1 id="about-title">About StatXavi</h1>
      </header>

      <div className="about-sections">
        <section className="methodology-card about-section">
          <h2>Mission</h2>
          <p>
            StatXavi is a scouting-oriented soccer analytics platform built for
            fans who want to explore player profiles, compare historical performances, and
            discover potential transfer targets for their favorite clubs.
          </p>
          <p>
            Powered by open-source, event-level data from StatsBomb, StatXavi
            uses Principal Component Analysis (PCA) to identify statistically
            similar players based on engineered season-level performance
            metrics, including per-90 statistics.
          </p>
          <p>
            Through interactive visualizations, position-relative player
            profiles, and similarity recommendations, the platform makes
            data-driven player exploration accessible to the most devoted fans.
          </p>
        </section>

        <section className="methodology-card about-section">
          <h2>Data Coverage</h2>
          <div className="about-table-wrapper">
            <table className="profile-table about-coverage-table">
              <thead>
                <tr>
                  <th scope="col">Season / Year</th>
                  <th scope="col">Competitions</th>
                </tr>
              </thead>
              <tbody>
                {competitions.map(({ season, competitions: names }) => (
                  <tr key={season}>
                    <th scope="row">{season}</th>
                    <td>{names}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="about-attribution">
            Data courtesy of{" "}
            <a
              href="https://github.com/statsbomb/open-data"
              target="_blank"
              rel="noopener noreferrer"
            >
              StatsBomb Open Data
            </a>
            .
          </p>
        </section>

        <section className="methodology-card about-section about-developer">
          <h2>About the Developer</h2>
          <p>
            StatXavi was developed by <strong>Teddy Kolios</strong>, an aspiring
            data professional with a background in software engineering and a
            Master’s degree in Computational Analysis and Public Policy.
          </p>
          <p>
            He is a lifelong Manchester United supporter.
          </p>
        </section>
      </div>

      <aside className="methodology-note about-disclaimer">
        <p>
          StatXavi is an independent, exploratory analytics project. Its
          similarity recommendations reflect statistical playing profiles
          rather than overall player quality or scouting judgments.
        </p>
      </aside>
    </main>
  );
}

export default About;
