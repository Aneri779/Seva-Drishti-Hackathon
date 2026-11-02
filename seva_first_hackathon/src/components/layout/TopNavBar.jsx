import { Link, useLocation } from 'react-router-dom';

const NAV_LINKS = [
  { label: 'Advisory Map',       href: '/dashboard' },
  { label: 'Chainage Registry',  href: '/chainage-registry' },
  { label: 'Convoy Routing',     href: '/convoy-routing' },
  { label: 'Mass Alerts',        href: '/notifications' },
  { label: 'Flood Bulletin',     href: '/bulletin' },
  { label: 'Field Dispatch',     href: '/dispatch' },
  { label: 'Admin Settings',     href: '/admin' },
];

export default function TopNavBar() {
  const { pathname } = useLocation();

  return (
    <header className="bg-surface-container-lowest/90 backdrop-blur-md sticky top-0 z-50 border-b border-outline-variant/30 shadow-sm">
      <div className="flex justify-between items-center w-full px-6 py-3 max-w-7xl mx-auto">

        {/* Brand */}
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded border border-primary/40 bg-surface-container-high flex items-center justify-center text-primary shadow-[0_0_12px_rgba(76,215,246,0.25)]">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>radar</span>
          </div>
          <div>
            <div className="text-sm font-bold text-on-surface tracking-tight flex items-center gap-2">
              SAR-Drishti | R&amp;B Dept, Govt of Gujarat
              <span className="hidden xl:inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-mono bg-tertiary/10 text-tertiary border border-tertiary/30">
                Sentinel-1 C-SAR
              </span>
            </div>
            <div className="font-mono text-[10px] text-on-surface-variant tracking-wider">
              SATELLITE HIGHWAY SUBMERGENCE TELEMETRY
            </div>
          </div>
        </Link>

        {/* Nav Links */}
        <nav className="hidden lg:flex items-center gap-4 xl:gap-5">
          {NAV_LINKS.map(({ label, href }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                to={href}
                className={`font-mono text-xs transition-colors duration-150 ${
                  isActive ? 'text-primary font-bold border-b-2 border-primary pb-0.5' : 'text-on-surface-variant hover:text-primary'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Trailing Actions */}
        <div className="flex items-center gap-2.5">
          <Link
            to="/login"
            className="px-3 py-1.5 rounded border border-primary/40 bg-surface-container hover:bg-surface-container-high text-primary font-mono text-xs transition-all active:scale-95 flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-sm">lock</span>
            <span>Login</span>
          </Link>
          <Link
            to="/register"
            className="px-3 py-1.5 rounded bg-primary text-surface-container-lowest font-mono text-xs font-bold hover:bg-surface-tint active:scale-95 transition-all flex items-center gap-1 shadow-sm"
          >
            <span className="material-symbols-outlined text-sm">badge</span>
            <span>Register Unit</span>
          </Link>
        </div>

      </div>
    </header>
  );
}
