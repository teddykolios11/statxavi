function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="site-footer-content">
        <div className="footer-branding">
          <strong className="footer-brand">StatXavi</strong>
          <p>Explore the numbers behind the beautiful game.</p>
        </div>
        <p className="footer-attribution">
          Powered by{" "}
          <a
            href="https://github.com/statsbomb/open-data"
            target="_blank"
            rel="noopener noreferrer"
          >
            StatsBomb Open Data
          </a>
        </p>
        <nav className="footer-links" aria-label="Developer links">
          <a
            href="https://github.com/teddykolios11"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/teddykolios/"
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
        </nav>
        <p className="footer-copyright">© {currentYear} StatXavi</p>
      </div>
    </footer>
  );
}

export default Footer;
