import { Link, useLocation } from 'react-router-dom';

export default function TacticalHeader({ title = "SAR HYDRO-OPS // SENTINEL-1 TELEMETRY", subtitle = "" }) {
  const location = useLocation();
  const currentPath = location.pathname;

  const navLinks = [
    { label: "GIS VIEWPORT", path: "/dashboard" },
    { label: "BACKSCATTER DENSITY", path: "/backscatter" },
    { label: "CHAINAGE REGISTRY", path: "/chainage-registry" },
    { label: "CONVOY ROUTING", path: "/convoy-routing" },
    { label: "MASS NOTIFICATION", path: "/notifications" },
    { label: "BULLETIN REPORTS", path: "/bulletin" },
    { label: "FIELD DISPATCH", path: "/dispatch" },
    { label: "ADMIN REPOSITORY", path: "/admin" },
  ];

  return (
    <header className="flex justify-between items-center w-full px-4 py-2 border-b border-outline-variant bg-surface-container-low shrink-0 z-30 select-none">
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <span className="material-symbols-outlined text-primary text-xl">satellite_alt</span>
          <div className="flex flex-col">
            <span className="text-sm font-bold text-primary tracking-wider whitespace-nowrap">
              {title}
            </span>
            {subtitle ? (
              <span className="text-[10px] font-mono text-outline">{subtitle}</span>
            ) : (
              <span className="text-[10px] font-mono text-outline">STATE EMERGENCY OPS // BISAG-N & ISRO SYNC</span>
            )}
          </div>
        </Link>
        <div className="hidden 2xl:flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface-container border border-outline-variant text-[10px] font-mono">
          <span className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
          <span className="text-tertiary">S1B DESC 136 SYNCED</span>
        </div>
      </div>

      {/* Center Nav Links with active indicator */}
      <nav className="hidden lg:flex items-center gap-3 xl:gap-5">
        {navLinks.map((link) => {
          const isActive = currentPath === link.path;
          return (
            <Link
              key={link.path}
              to={link.path}
              className={`font-mono text-xs px-2 py-1 transition-colors duration-150 rounded ${
                isActive
                  ? "border-b-2 border-primary text-primary font-bold bg-surface-container/50"
                  : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      {/* Trailing Controls */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1 border-r border-outline-variant pr-2 text-on-surface-variant">
          <Link to="/backscatter" className="p-1 hover:text-on-surface hover:bg-surface-container rounded" title="Backscatter Analysis">
            <span className="material-symbols-outlined text-[17px]">radar</span>
          </Link>
          <Link to="/chainage-registry" className="p-1 hover:text-on-surface hover:bg-surface-container rounded" title="Vector Layers">
            <span className="material-symbols-outlined text-[17px]">layers</span>
          </Link>
          <Link to="/notifications" className="p-1 text-secondary hover:text-on-surface hover:bg-surface-container rounded relative" title="Alert Broadcasts">
            <span className="material-symbols-outlined text-[17px]">notifications_active</span>
            <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
          </Link>
          <Link to="/admin" className="p-1 hover:text-on-surface hover:bg-surface-container rounded" title="Settings / Config">
            <span className="material-symbols-outlined text-[17px]">settings</span>
          </Link>
        </div>
        <Link
          to="/"
          className="hidden sm:inline-flex items-center px-2 py-1 rounded border border-outline-variant text-[11px] font-mono text-on-surface hover:bg-surface-container-high transition-colors"
        >
          Public Portal
        </Link>
        <Link
          to="/dashboard"
          className="px-2.5 py-1 bg-primary text-surface-container-lowest font-mono text-[11px] font-bold rounded hover:bg-surface-tint active:scale-95 transition-all flex items-center gap-1 shadow-sm"
        >
          <span className="material-symbols-outlined text-sm">dashboard</span>
          <span>Command GIS</span>
        </Link>
        <div className="w-7 h-7 rounded border border-primary/40 bg-surface-container-high flex items-center justify-center text-primary text-[10px] font-bold font-mono">
          SEOC
        </div>
      </div>
    </header>
  );
}
