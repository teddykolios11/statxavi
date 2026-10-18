import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import About from "./About.jsx";
import Footer from "./Footer.jsx";
import Header from "./Header.jsx";
import Methodology from "./Methodology.jsx";
import { API_BASE_URL } from "./config.js";
import "./index.css";

const defaultSeason = "2015-2016";
const defaultSeasons = [
  { id: defaultSeason, label: "2015/16 European Leagues" },
];

function StatXavi() {
  const [season, setSeason] = useState(defaultSeason);
  const [seasons, setSeasons] = useState(defaultSeasons);
  const [seasonError, setSeasonError] = useState("");
  const [activeTab, setActiveTab] = useState("players");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    fetch(`${API_BASE_URL}/seasons`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load available datasets.");
        }
        return response.json();
      })
      .then((result) => {
        if (!Array.isArray(result.seasons) || result.seasons.length === 0) {
          throw new Error("The server returned no available datasets.");
        }
        if (active) {
          setSeasons(result.seasons);
          setSeasonError("");
        }
      })
      .catch((error) => {
        if (active && error.name !== "AbortError") {
          setSeasonError(error.message);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  return (
    <>
      <Header
        season={season}
        seasons={seasons}
        seasonError={seasonError}
        onSeasonChange={setSeason}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      <App key={season} season={season} activeTab={activeTab} />
      <Methodology activeTab={activeTab} />
      <About activeTab={activeTab} />
      <Footer />
    </>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <StatXavi />
  </React.StrictMode>,
);
