import xaviLogo from "../../images/spain_xavi.jpeg";

function Header({ season, seasons, seasonError, onSeasonChange }) {
  return (
    <header className="site-header">
      <div className="site-header-content">
        <a className="site-brand" href="/" aria-label="StatXavi home">
          <img className="site-brand-logo" src={xaviLogo} alt="" />
          <span>StatXavi</span>
        </a>
        <nav className="site-navigation" aria-label="Main navigation">
          <label className="dataset-selector">
            <span className="visually-hidden">Season or tournament</span>
            <select
              className="dataset-select"
              value={season}
              aria-label="Select season or tournament"
              onChange={(event) => onSeasonChange(event.target.value)}
            >
              {seasons.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.label}
                </option>
              ))}
            </select>
          </label>
          {seasonError && (
            <span className="dataset-selector-error" role="alert">
              {seasonError}
            </span>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;
