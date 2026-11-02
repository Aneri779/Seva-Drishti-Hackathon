import { Link, useLocation } from 'react-router-dom';

export default function TacticalSideRail({ compact = false }) {
  const location = useLocation();
  const currentPath = location.pathname;

  const items = [
    { label: "SAR Orbit", icon: "radar", path: "/dashboard" },
    { label: "VV/VH Co-Pol", icon: "show_chart", path: "/backscatter" },
    { label: "DEM Slicing", icon: "terrain", path: "/backscatter" },
    { label: "Chainage Reg", icon: "alt_route", path: "/chainage-registry" },
    { label: "Otsu Engine", icon: "tune", path: "/backscatter" },
    { label: "Convoy Routes", icon: "route", path: "/convoy-routing" },
    { label: "Breach Alert", icon: "warning", path: "/dispatch", isAlert: true, badge: "4" },
    { label: "Mass Alert", icon: "broadcast_on_personal", path: "/notifications" },
    { label: "Bulletins", icon: "description", path: "/bulletin" },
    { label: "Settings / Admin", icon: "settings", path: "/admin" },
  ];

  if (compact) {
    return (
      <aside className="flex flex-col justify-between h-full w-14 shrink-0 py-2 border-r border-outline-variant bg-surface-container z-40 select-none">
        <div className="flex flex-col items-center gap-1">
          <Link
            to="/dashboard"
            className="w-10 h-10 rounded flex flex-col items-center justify-center bg-surface-container-lowest border border-outline-variant text-primary mb-2 hover:border-primary transition-colors"
            title="Node 04-Alpha"
          >
            <span className="material-symbols-outlined text-[18px]">radar</span>
            <span className="text-[9px] font-mono font-bold">N-04</span>
          </Link>
          {items.map((it) => {
            const isActive = currentPath === it.path;
            return (
              <Link
                key={it.label}
                to={it.path}
                className={`w-10 h-10 rounded flex flex-col items-center justify-center transition-colors relative ${
                  isActive
                    ? "bg-primary-container/20 text-primary border-l-2 border-primary"
                    : it.isAlert
                    ? "text-error hover:bg-surface-container-high"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
                }`}
                title={it.label}
              >
                <span className="material-symbols-outlined text-[18px]">{it.icon}</span>
                <span className="text-[8px] font-mono leading-none">{it.label.slice(0, 5)}</span>
                {it.isAlert && <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>}
              </Link>
            );
          })}
        </div>
        <div className="flex flex-col items-center gap-1 pt-1 border-t border-outline-variant">
          <Link to="/admin" className="w-10 h-10 rounded flex items-center justify-center text-on-surface-variant hover:text-on-surface" title="Settings">
            <span className="material-symbols-outlined text-[18px]">settings</span>
          </Link>
        </div>
      </aside>
    );
  }

  return (
    <aside className="flex flex-col justify-between h-full w-56 py-3 border-r border-outline-variant bg-surface-container shrink-0 z-20 select-none overflow-y-auto">
      <div>
        {/* Rail Header */}
        <div className="px-3 pb-2 border-b border-outline-variant">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-xl">radar</span>
            <div>
              <div className="text-xs font-mono font-bold text-primary">NODE 04-ALPHA</div>
              <div className="text-[10px] font-mono text-outline">CHAINAGE KM 42+800</div>
            </div>
          </div>
        </div>

        {/* Rail Navigation Tabs */}
        <nav className="flex-1 py-2 space-y-0.5">
          {items.map((it) => {
            const isActive = currentPath === it.path;
            return (
              <Link
                key={it.label}
                to={it.path}
                className={`flex items-center justify-between px-3 py-1.5 transition-colors text-xs font-mono ${
                  isActive
                    ? "bg-primary-container/20 text-primary border-l-2 border-primary font-bold"
                    : it.isAlert
                    ? "text-error hover:bg-surface-container-highest"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <span className="material-symbols-outlined text-[16px]">{it.icon}</span>
                  <span>{it.label}</span>
                </div>
                {it.badge && (
                  <span className="bg-error-container text-error text-[10px] px-1.5 py-0.2 rounded font-mono font-bold">
                    {it.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Side Mini Status Card */}
        <div className="mx-2 mt-2 p-2 bg-surface-container-lowest border border-outline-variant rounded">
          <div className="flex justify-between text-[10px] font-mono text-on-surface-variant mb-1">
            <span>SAR COHERENCE</span>
            <span className="text-primary font-bold">γ = 0.21</span>
          </div>
          <div className="w-full bg-surface-container-high h-1 rounded-full overflow-hidden">
            <div className="bg-primary h-full w-[21%]"></div>
          </div>
          <div className="mt-2 flex justify-between text-[10px] font-mono text-on-surface-variant">
            <span>WATER DEPTH</span>
            <span className="text-error font-bold">+0.48m</span>
          </div>
        </div>

        {/* Action Button */}
        <div className="px-2 mt-3">
          <Link
            to="/backscatter"
            className="w-full bg-primary-container text-on-primary-container hover:bg-surface-tint font-mono text-xs py-1.5 px-2 rounded active:scale-[0.98] transition-transform flex items-center justify-center gap-1 font-bold text-center"
          >
            <span className="material-symbols-outlined text-[15px]">bolt</span>
            <span>RUN OTSU SOLVER</span>
          </Link>
        </div>
      </div>

      {/* Rail Footer */}
      <div className="border-t border-outline-variant pt-2 flex flex-col gap-1">
        <Link
          to="/admin"
          className="text-on-surface-variant flex items-center px-3 py-1 hover:text-on-surface hover:bg-surface-container-highest transition-colors text-xs font-mono gap-2"
        >
          <span className="material-symbols-outlined text-[16px]">settings</span>
          <span>System Settings</span>
        </Link>
        <div className="px-3 py-1 flex items-center justify-between border-t border-outline-variant/60 mt-1">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-tertiary"></div>
            <span className="font-mono text-[10px] text-on-surface-variant">C-BAND SYNCED</span>
          </div>
          <span className="font-mono text-[10px] text-primary">0.04 ms</span>
        </div>
      </div>
    </aside>
  );
}
