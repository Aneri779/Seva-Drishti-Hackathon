// PAGE 4: SEOC Command Center / Advisory Map Dashboard (Live Gujarat Telemetry)
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [selectedPass, setSelectedPass] = useState('');
  const [activeDistrict, setActiveDistrict] = useState('');

  // Live clock
  useEffect(() => {
    const el = document.getElementById('telemetryClock');
    if (!el) return;
    const tick = () => {
      const n = new Date();
      el.textContent = `${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}:${String(n.getSeconds()).padStart(2,'0')} IST`;
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  // Live API Hooks with real-time polling every 10 seconds
  const { data: alertsData } = useApi(() => api.get(`/alerts${activeDistrict ? `?district=${encodeURIComponent(activeDistrict)}` : ''}`), [activeDistrict], 10000);
  const { data: scenesData } = useApi(() => api.get('/scenes'), [], 30000);
  const { data: statsData } = useApi(() => api.get(`/stats/summary${activeDistrict ? `?district=${encodeURIComponent(activeDistrict)}` : ''}`), [activeDistrict], 10000);
  const { data: districtsData } = useApi(() => api.get('/meta/districts'), []);
  const { data: roadClassesData } = useApi(() => api.get('/stats/road-classes'), [], 15000);

  const alerts = alertsData || [];
  const scenes = scenesData || [];
  const stats = statsData || {
    monitored_km: 18420,
    submerged_segments: 14,
    washouts: 3,
    deployed_teams: 18,
    critical_alerts: 4
  };
  const districts = districtsData || [];
  const roadClasses = roadClassesData || [];

  return (
    <div className="flex flex-col">
      {/* ── Emergency alert ticker ───────────────────── */}
      <aside className="w-full bg-error-container text-on-error-container border-b border-error/40 px-6 py-2">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3 text-label-code font-label-code text-xs">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-error text-surface-container-lowest font-bold animate-pulse uppercase tracking-wider text-[11px]">
              <span className="material-symbols-outlined text-xs">warning</span>
              FLASH LEVEL-4
            </span>
            <span className="font-bold tracking-tight">CYCLONE EMERGENCY ADVISORY: SEVERE SURGE WARNING - SAURASHTRA &amp; KUTCH COAST</span>
            <span className="hidden lg:inline text-on-error-container/80 text-body-sm font-body-sm">| Synthetic Aperture Radar detects acute overtopping across NH-51 &amp; SH-25 Miyani causeway.</span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span className="flex items-center gap-1.5 text-on-error-container font-label-code">
              <span className="material-symbols-outlined text-xs">schedule</span>
              LIVE: <span className="font-bold ml-1" id="telemetryClock">IST</span>
            </span>
          </div>
        </div>
      </aside>

      {/* ── Actions sub-header ───────────────────────── */}
      <section className="bg-surface-container-low border-b border-outline-variant/30 py-3 px-6">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-surface-container px-3 py-1.5 rounded border border-outline-variant/30 text-label-code font-label-code text-xs">
              <span className="text-on-surface-variant flex items-center gap-1">
                <span className="material-symbols-outlined text-xs text-primary">satellite_alt</span>
                Active Orbit:
              </span>
              <select
                value={selectedPass}
                onChange={e => setSelectedPass(e.target.value)}
                className="bg-transparent text-primary font-bold focus:outline-none border-none p-0 cursor-pointer text-xs"
              >
                {scenes.map(s => (
                  <option key={s.id} value={s.id} className="bg-surface-container text-on-surface">{s.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <button 
              onClick={() => navigate(activeDistrict ? `/bulletin?district=${encodeURIComponent(activeDistrict)}` : '/bulletin')}
              className="px-3.5 py-1.5 rounded bg-primary-container text-on-primary-container text-label-code font-label-code text-xs font-bold flex items-center gap-1.5 hover:brightness-110 shadow transition-all"
            >
              <span className="material-symbols-outlined text-sm">download</span>
              Generate District Flood Bulletin
            </button>
          </div>
        </div>
      </section>

      {/* ── 3-column main area ───────────────────────── */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-5 grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">

        {/* LEFT SIDEBAR: Gujarat Filters */}
        <aside className="lg:col-span-3 space-y-4">
          <div className="hud-box bg-surface-container-lowest/80 backdrop-blur-md rounded border border-outline-variant/30 p-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/30">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-base">filter_alt</span>
                <h2 className="text-label-code font-label-code font-bold text-on-surface uppercase tracking-wider text-xs">Coastal Districts (Gujarat)</h2>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {districts.slice(0, 8).map(d => (
                <button
                  key={d.id}
                  onClick={() => setActiveDistrict(d.name)}
                  className={`px-2.5 py-1 rounded text-label-code font-label-code text-[11px] border transition-all ${
                    activeDistrict === d.name ? 'bg-primary text-surface-container-lowest font-bold border-primary' : 'bg-surface-container border-outline-variant/30 text-on-surface'
                  }`}
                >
                  {d.name}
                </button>
              ))}
            </div>

            {/* Road classification tier */}
            <div className="mt-4 pt-3 border-t border-outline-variant/20">
              <span className="text-label-meta font-label-meta text-on-surface-variant block mb-2">ROAD CLASSIFICATION TIER</span>
              <div className="grid grid-cols-2 gap-1.5 text-label-code font-label-code text-[11px]">
                {roadClasses.map((rc) => (
                  <button key={rc.name} className={`px-2 py-1.5 rounded text-left flex items-center justify-between ${rc.active ? 'bg-surface-container-high text-primary border border-primary/40' : 'bg-surface-container text-on-surface-variant border border-outline-variant/30'}`}>
                    <span>{rc.name}</span>
                    <span className={`text-[10px] px-1 rounded ${rc.active ? 'bg-primary/20' : 'bg-surface-container-highest'}`}>{rc.count}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* CENTER: Radar Corridor Display */}
        <section className="lg:col-span-6 space-y-3" id="advisory-map">
          <div className="relative w-full h-[620px] rounded bg-surface-container-lowest border border-outline-variant/40 overflow-hidden shadow-2xl flex flex-col">
            <div className="relative flex-1 w-full h-full bg-[#070b14] overflow-hidden select-none">
              <div className="absolute inset-0 opacity-20 pointer-events-none" style={{backgroundImage:'radial-gradient(#22d3ee 0.75px,transparent 0.75px),radial-gradient(#22d3ee 0.75px,#070b14 0.75px)',backgroundSize:'32px 32px',backgroundPosition:'0 0,16px 16px'}}></div>

              {/* Gujarat Coastline SVG Representation */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1000 800" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M 120,40 Q 280,30 450,90 T 780,120 L 980,180 L 1000,790 L 400,790 L 320,680 L 210,540 L 80,480 L 40,320 L 110,240 Z" fill="#0d1424" stroke="#1f2d47" strokeWidth="1.5"/>
                <path d="M 0,210 Q 150,220 280,260 T 420,290 C 370,330 250,340 180,330 T 40,340 Z" fill="#06182c" stroke="#00cbe6" strokeOpacity="0.4" strokeWidth="2"/>
                <path d="M 40,340 C 120,350 240,370 280,440 T 260,570 T 360,680 T 520,710 T 640,660 T 700,560 T 740,490" fill="none" stroke="#22d3ee" strokeDasharray="6 3" strokeOpacity="0.5" strokeWidth="2.5"/>

                {/* Submerged Highway Corridors */}
                <path d="M 940,320 L 720,380 L 520,410 L 380,420" stroke="#10b981" strokeWidth="3.5" strokeLinecap="round"/>
                <path d="M 235,485 L 260,515" stroke="#ef4444" strokeWidth="5" strokeLinecap="round" className="animate-pulse" />
                <path d="M 340,270 L 375,262" stroke="#ef4444" strokeWidth="5" strokeLinecap="round" />
              </svg>

              {/* Callout popover */}
              <div className="absolute top-[44%] left-[30%] max-w-[285px] w-full z-20 bg-surface-container-low/95 backdrop-blur-md rounded border border-error/50 p-3 shadow-2xl">
                <div className="flex items-start justify-between border-b border-error/30 pb-1.5 mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>
                    <span className="text-label-code font-label-code font-bold text-error text-[11px]">CRITICAL BREACH CUT-OFF</span>
                  </div>
                  <span className="text-[10px] font-label-code text-on-surface-variant">Km 44.200</span>
                </div>
                <div className="space-y-1 text-label-code font-label-code text-[11px]">
                  <div className="font-bold text-on-surface text-xs">SH-25: Miyani Causeway</div>
                  <div className="flex justify-between text-on-surface-variant"><span>SAR Depth:</span><span className="text-error font-bold">+42 cm Submerged (estimated)</span></div>
                  <div className="flex justify-between text-on-surface-variant"><span>Backscatter Δ:</span><span className="text-secondary">-22.4 dB (Water)</span></div>
                  <div className="pt-1.5 mt-1 border-t border-outline-variant/30 text-[10px] font-body-sm text-tertiary">
                    <span className="font-bold">Diversion:</span> SH-27 Ranavav - Bhanvad Clear
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* RIGHT SIDEBAR: KPIs & Realtime Alerts Feed */}
        <aside className="lg:col-span-3 space-y-4">
          <div className="grid grid-cols-2 gap-2.5">
            {[
              { label:'MONITORED GRID', val:`${stats.monitored_km.toLocaleString()} km`, sub:'Gujarat Highway Net', icon:'traffic', color:'primary', border:'border-outline-variant/30' },
              { label:'SUBMERGED SEGMENTS', val:`${stats.submerged_segments} Segs`, sub:'Zero vehicular pass', icon:'crisis_alert', color:'error', border:'border-error/50' },
              { label:'SCOUR BREACHES', val:`${stats.washouts} Washouts`, sub:'Structural Fracture', icon:null, color:'error', border:'border-error/70', ping:true },
              { label:'DEPLOYED TEAMS', val:`${stats.deployed_teams} Units`, sub:'R&B / SDRF Rapid Unit', icon:'fire_truck', color:'tertiary', border:'border-tertiary/40' },
            ].map(({ label, val, sub, icon, color, border, ping }) => (
              <div key={label} className={`hud-box bg-surface-container-lowest/85 backdrop-blur-md p-3 rounded border ${border}`}>
                <div className="flex items-center justify-between">
                  <span className={`text-label-meta font-label-meta text-${color} text-[10px] font-bold`}>{label}</span>
                  {icon ? <span className={`material-symbols-outlined text-${color} text-xs`}>{icon}</span> : ping && <span className={`w-2 h-2 rounded-full bg-${color} animate-ping`}></span>}
                </div>
                <div className={`text-headline-sm font-telemetry-metric text-${color} mt-1`}>{val}</div>
                <div className="text-[10px] font-label-code text-on-surface-variant">{sub}</div>
              </div>
            ))}
          </div>

          {/* Live Alerts Feed from API */}
          <div className="hud-box bg-surface-container-lowest/85 backdrop-blur-md rounded border border-outline-variant/30 p-3.5 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/30">
              <div className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-error text-base">report</span>
                <h2 className="text-label-code font-label-code font-bold text-on-surface uppercase tracking-wider text-xs">Live Chainage Breaches</h2>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-label-code bg-error/20 text-error font-bold">Realtime SAR Log</span>
            </div>
            <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
              {alerts.map(({ id, road, ago, desc, action, zone, border }) => (
                <div key={id || road} className={`p-2.5 rounded bg-surface-container border-l-2 ${border} border-y border-r border-outline-variant/20 space-y-1.5`}>
                  <div className="flex items-start justify-between">
                    <span className="text-xs font-label-code font-bold text-on-surface">{road}</span>
                    <span className="text-[10px] font-label-code text-on-surface-variant">{ago}</span>
                  </div>
                  <p className="text-[11px] font-body-sm text-on-surface leading-snug">{desc}</p>
                  <div className="pt-1 flex items-center justify-between">
                    <span className="text-[10px] font-label-code text-outline">{zone}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
