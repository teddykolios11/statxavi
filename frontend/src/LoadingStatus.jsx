import { useEffect, useState } from "react";

function LoadingStatus({ isLoading, error, onRetry }) {
  const [messageStage, setMessageStage] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setMessageStage(0);
      return undefined;
    }

    setMessageStage(0);
    const playerDataTimer = window.setTimeout(() => setMessageStage(1), 3000);
    const serverTimer = window.setTimeout(() => setMessageStage(2), 10000);

    return () => {
      window.clearTimeout(playerDataTimer);
      window.clearTimeout(serverTimer);
    };
  }, [isLoading]);

  if (error) {
    return (
      <div className="loading-status loading-status-error" role="alert">
        <p>We couldn&apos;t load the player data. Please try again.</p>
        <button
          className="compare-button loading-retry-button"
          type="button"
          onClick={onRetry}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!isLoading) {
    return null;
  }

  const message =
    messageStage === 2
      ? "Connecting to StatXavi’s analytics server. This may take up to a minute on the first visit."
      : messageStage === 1
        ? "Loading player data…"
        : "";

  return (
    <div className="loading-status" role="status" aria-live="polite">
      <span className="loading-spinner" aria-hidden="true" />
      {message ? (
        <span>{message}</span>
      ) : (
        <span className="visually-hidden">Loading player data</span>
      )}
    </div>
  );
}

export default LoadingStatus;
