// PAGE 8: Relief Logistics & Convoy Safe Routing (Live Gujarat Routing)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function ConvoyRouting() {
  const [origin, setOrigin] = useState('Gandhinagar State EOC Depot');
  const [destination, setDestination] = useState('Porbandar - Miyani Creek Sector');
  const [vehicle, setVehicle] = useState('NDRF Boats Truck');
  const [routingData, setRoutingData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleComputeRoute = async () => {
    setLoading(true);
    try {
      const res = await api.post('/routes', {
        origin,
        destination,
        vehicle_profile: vehicle
      });
      setRoutingData(res);
      showToast('Live corridor computed via Sentinel-1 SAR & DEM road status', 'success');
    } catch (e) {
      showToast(e.message || 'Routing computation failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const safeRoute = routingData?.safe_route;
  const blockedRoute = routingData?.blocked_route;
  const blockedChainages = routingData?.blocked_chainages || [];

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // SENTINEL-1 TELEMETRY"
        subtitle="DISASTER RELIEF LOGISTICS & EMERGENCY CONVOY ROUTING (રાહત બચાવ રૂટ પ્લાનર)"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail />

        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* LEFT: Planner Panel */}
          <aside className="w-full md:w-[420px] border-r border-outline-variant bg-surface-container-low flex flex-col justify-between shrink-0 overflow-y-auto z-20">
            <div>
              <div className="p-3 border-b border-outline-variant bg-surface-container flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-xl">alt_route</span>
                  <div>
                    <h2 className="text-xs font-bold text-on-surface uppercase">CONVOY MISSION PLANNER (GUJARAT)</h2>
                    <p className="text-[10px] font-mono text-outline">NDRF 6TH BN // STATE RELIEF LOGISTICS</p>
                  </div>
                </div>
                <span className="px-1.5 py-0.5 rounded border border-tertiary/40 bg-tertiary/10 text-tertiary text-[9px] font-mono font-bold">
                  COASTAL RELIEF
                </span>
              </div>

              {/* Form */}
              <div className="p-3 space-y-3 border-b border-outline-variant text-xs font-mono">
                <div>
                  <label className="text-[10px] text-on-surface-variant flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                    ORIGIN (DEPOT)
                  </label>
                  <input
                    className="w-full bg-surface-container-lowest border border-outline-variant rounded p-1.5 mt-1 text-on-surface text-xs focus:outline-none focus:border-primary"
                    value={origin}
                    onChange={e => setOrigin(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-[10px] text-on-surface-variant flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
                    DESTINATION (CUT-OFF REGION)
                  </label>
                  <input
                    className="w-full bg-surface-container-lowest border border-outline-variant rounded p-1.5 mt-1 text-on-surface text-xs focus:outline-none focus:border-primary"
                    value={destination}
                    onChange={e => setDestination(e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-[10px] text-on-surface-variant block mb-1">CONVOY FLEET VEHICLE PROFILE</label>
                  <div className="grid grid-cols-2 gap-1.5">
                    <button
                      type="button"
                      onClick={() => setVehicle('NDRF Boats Truck')}
                      className={`p-2 rounded border text-left flex flex-col justify-between ${
                        vehicle === 'NDRF Boats Truck'
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-outline-variant bg-surface-container text-on-surface-variant hover:border-outline'
                      }`}
                    >
                      <span className="font-bold text-[11px]">NDRF Boats Truck</span>
                      <span className="text-[9px] opacity-75">Max clearance 65 cm</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setVehicle('Medical Relief')}
                      className={`p-2 rounded border text-left flex flex-col justify-between ${
                        vehicle === 'Medical Relief'
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-outline-variant bg-surface-container text-on-surface-variant hover:border-outline'
                      }`}
                    >
                      <span className="font-bold text-[11px]">Medical Relief</span>
                      <span className="text-[9px] opacity-75">Standard ambulance 25 cm</span>
                    </button>
                  </div>
                </div>

                <button
                  onClick={handleComputeRoute}
                  disabled={loading}
                  className="w-full py-2.5 rounded bg-primary text-surface-container-lowest font-bold text-xs uppercase tracking-wider hover:bg-surface-tint shadow active:scale-95 transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-sm">route</span>
                  {loading ? 'COMPUTING CORRIDOR...' : 'COMPUTE SAFE CONVOY CORRIDOR'}
                </button>
              </div>

              {/* Real-time Blocked Chainages from PostgreSQL */}
              <div className="p-3 font-mono">
                <span className="text-[10px] text-outline uppercase font-bold tracking-wider block mb-2">
                  MONITORED BREACH SECTORS ({blockedChainages.length})
                </span>
                <div className="space-y-1.5">
                  {blockedChainages.length === 0 ? (
                    <div className="text-[11px] text-on-surface-variant">Click Compute to evaluate corridor constraints.</div>
                  ) : (
                    blockedChainages.map((b, idx) => (
                      <div key={idx} className="p-2 rounded border border-error/40 bg-error/10 text-xs">
                        <div className="flex items-center justify-between font-bold">
                          <span className="text-error">{b.road}</span>
                          <span className="text-[10px] text-error uppercase">{b.status}</span>
                        </div>
                        <div className="text-[11px] text-on-surface mt-0.5">{b.chainage} ({b.district})</div>
                        <div className="text-[10px] text-on-surface-variant mt-0.5">Submergence: {b.depth}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </aside>

          {/* RIGHT: Route Comparison Visualizer */}
          <main className="flex-1 bg-surface-container-lowest flex flex-col p-4 md:p-6 overflow-y-auto font-mono">
            {!routingData ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-outline-variant rounded-xl bg-surface-container-low">
                <span className="material-symbols-outlined text-5xl text-primary mb-3">navigation</span>
                <h3 className="text-base font-bold text-on-surface">No Corridor Computed Yet</h3>
                <p className="text-xs text-on-surface-variant max-w-md mt-1">
                  Click <b>"Compute Safe Convoy Corridor"</b> to evaluate live Sentinel-1 SAR flood boundaries and DEM water level profiles across the Gujarat highway network.
                </p>
              </div>
            ) : (
              <div className="space-y-4 max-w-4xl mx-auto w-full">
                {/* Safe vs Blocked Route Comparison Cards */}
                <div className="grid md:grid-cols-2 gap-4">
                  {/* Safe Detour Corridor */}
                  <div className="p-4 rounded-xl border border-green-500/50 bg-green-950/20 shadow-lg space-y-3">
                    <div className="flex items-center justify-between border-b border-green-500/30 pb-2">
                      <span className="font-bold text-xs text-green-400 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-sm">verified</span>
                        {safeRoute?.title}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-300 font-bold text-[10px]">
                        RECOMMENDED
                      </span>
                    </div>

                    <div className="text-xs text-on-surface font-semibold">{safeRoute?.via}</div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                      <div className="p-2 rounded bg-surface-container-low border border-outline-variant/40">
                        <span className="text-[10px] text-outline block">TOTAL DISTANCE</span>
                        <span className="font-bold text-on-surface">{safeRoute?.distance_km} km</span>
                      </div>
                      <div className="p-2 rounded bg-surface-container-low border border-outline-variant/40">
                        <span className="text-[10px] text-outline block">ESTIMATED TRANSIT</span>
                        <span className="font-bold text-green-400">{safeRoute?.eta_str}</span>
                      </div>
                    </div>

                    <div className="text-[11px] text-on-surface-variant space-y-1">
                      <div>● Elevation profile: <span className="text-on-surface font-semibold">{safeRoute?.submergence_m}</span></div>
                      <div>● Clearance: <span className="text-green-400 font-semibold">{safeRoute?.clearance_status}</span></div>
                      <div>● Navigability: <span className="text-green-400 font-semibold">{safeRoute?.passable_pct}</span></div>
                    </div>
                  </div>

                  {/* Blocked Coastal Route */}
                  <div className="p-4 rounded-xl border border-error/50 bg-error/10 shadow-lg space-y-3">
                    <div className="flex items-center justify-between border-b border-error/30 pb-2">
                      <span className="font-bold text-xs text-error flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-sm">dangerous</span>
                        {blockedRoute?.title}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-error/20 text-error font-bold text-[10px]">
                        IMPASSABLE
                      </span>
                    </div>

                    <div className="text-xs text-on-surface font-semibold">{blockedRoute?.via}</div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                      <div className="p-2 rounded bg-surface-container-low border border-outline-variant/40">
                        <span className="text-[10px] text-outline block">DIRECT DISTANCE</span>
                        <span className="font-bold text-on-surface">{blockedRoute?.distance_km} km</span>
                      </div>
                      <div className="p-2 rounded bg-surface-container-low border border-outline-variant/40">
                        <span className="text-[10px] text-outline block">PROJECTED LOSS</span>
                        <span className="font-bold text-error">Severed / Cut-Off</span>
                      </div>
                    </div>

                    <div className="text-[11px] text-on-surface-variant space-y-1">
                      <div>● Flood Depth: <span className="text-error font-semibold">{blockedRoute?.submergence_m}</span></div>
                      <div>● Structural Status: <span className="text-error font-semibold">{blockedRoute?.clearance_status}</span></div>
                      <div>● Navigability: <span className="text-error font-semibold">{blockedRoute?.passable_pct}</span></div>
                    </div>
                  </div>
                </div>

                {/* Tactical Waypoint Nodes Display */}
                <div className="p-4 bg-surface-container rounded-xl border border-outline-variant text-xs space-y-2">
                  <div className="font-bold text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-base">hub</span>
                    Corridor Waypoint Telemetry (Gujarat Highway Mesh)
                  </div>
                  <div className="grid md:grid-cols-3 gap-2 text-[11px] text-on-surface-variant">
                    <div className="p-2 rounded bg-surface-container-lowest border border-outline-variant/30">
                      <b>Origin Hub:</b> Gandhinagar EOC (23.21°N, 72.63°E)
                    </div>
                    <div className="p-2 rounded bg-surface-container-lowest border border-outline-variant/30">
                      <b>Inland Ridge Detour:</b> Junagadh Ridge (21.52°N, 70.45°E)
                    </div>
                    <div className="p-2 rounded bg-surface-container-lowest border border-outline-variant/30">
                      <b>Safe Destination:</b> Porbandar Hub (21.64°N, 69.62°E)
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
