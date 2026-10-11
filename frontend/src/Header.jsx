import xaviLogo from "../../images/spain_xavi.jpeg";

function Header() {
  return (
    <header className="site-header">
      <div className="site-header-content">
        <a className="site-brand" href="/" aria-label="StatXavi home">
          <img className="site-brand-logo" src={xaviLogo} alt="" />
          <span>StatXavi</span>
        </a>
        <nav className="site-navigation" aria-label="Main navigation" />
      </div>
    </header>
  );
}

export default Header;
