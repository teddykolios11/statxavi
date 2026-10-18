import xaviLogo from "../../images/spain_xavi.jpeg";

function Header({
  season,
  seasons,
  seasonError,
  onSeasonChange,
  activeTab,
  onTabChange,
}) {
  function handleTabKeyDown(event) {
    const tabs = Array.from(
      event.currentTarget.parentElement.querySelectorAll('[role="tab"]'),
    );
    const currentIndex = tabs.indexOf(event.currentTarget);
    let nextIndex;

    switch (event.key) {
      case "ArrowRight":
        nextIndex = (currentIndex + 1) % tabs.length;
        break;
      case "ArrowLeft":
        nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        break;
      case "Home":
        nextIndex = 0;
        break;
      case "End":
        nextIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    event.preventDefault();
    tabs[nextIndex].focus();
    onTabChange(tabs[nextIndex].dataset.tab);
  }

  return (
    <header className="site-header">
      <div className="site-header-content">
        <a className="site-brand" href="/" aria-label="StatXavi home">
          <img className="site-brand-logo" src={xaviLogo} alt="" />
          <span>StatXavi</span>
        </a>
        <nav className="site-navigation" aria-label="Main navigation">
          <div className="site-tab-list" role="tablist" aria-label="Application">
            <button
              className="site-tab"
              type="button"
              role="tab"
              id="player-search-tab"
              data-tab="players"
              aria-selected={activeTab === "players"}
              aria-controls="player-search-panel"
              tabIndex={activeTab === "players" ? 0 : -1}
              onKeyDown={handleTabKeyDown}
              onClick={() => onTabChange("players")}
            >
              Player Search
            </button>
            <button
              className="site-tab"
              type="button"
              role="tab"
              id="methodology-tab"
              data-tab="methodology"
              aria-selected={activeTab === "methodology"}
              aria-controls="methodology-panel"
              tabIndex={activeTab === "methodology" ? 0 : -1}
              onKeyDown={handleTabKeyDown}
              onClick={() => onTabChange("methodology")}
            >
              Methodology
            </button>
            <button
              className="site-tab"
              type="button"
              role="tab"
              id="about-tab"
              data-tab="about"
              aria-selected={activeTab === "about"}
              aria-controls="about-panel"
              tabIndex={activeTab === "about" ? 0 : -1}
              onKeyDown={handleTabKeyDown}
              onClick={() => onTabChange("about")}
            >
              About
            </button>
          </div>
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
