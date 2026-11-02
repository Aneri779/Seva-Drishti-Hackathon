// PAGE 1: SAR-Drishti Home / Advisory Map
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import { showToast } from '../components/common/Toast';

export default function HomePage() {
  const navigate = useNavigate();
  const { data: corridorsData } = useApi(() => api.get('/advisories/corridors'), [], 15000);
  const corridors = corridorsData || [];
  const [origin, setOrigin] = useState('Jamnagar');
  const [destination, setDestination] = useState('Junagadh');
  const [highway, setHighway] = useState('GJ-SH-25');
  const [isVerifying, setIsVerifying] = useState(false);
  const [corridorResult, setCorridorResult] = useState({
    has_alert: true,
    status: 'SUBMERGENCE ALERT',
    highway: 'GJ-SH-25: Porbandar – Dwarka Coastal Highway',
    chainage_span: 'Chainage 42.100 km to 44.800 km (Miyani Creek Causeway Overtopped)',
    depth_text: 'Satellite SAR backscatter analysis confirms 28cm – 32cm standing water across both carriageways. Unsafe for passenger sedans and 2-wheelers.',
    detour_route: 'Approved R&B Safe Detour: Reroute via SH-27 Ranavav – Bhanvad Corridor.',
    detour_status: 'STATUS: ALL CLEAR • Radar Coherence: 0.98 (High Stability)',
    observed_at: 'Observed via Sentinel-1 SAR Overpass at 14:18 IST (12 mins ago)',
  });

  const handleVerifyCorridor = async () => {
    setIsVerifying(true);
    try {
      const res = await api.post('/routes/public-verify', { origin, destination, highway });
      setCorridorResult(res);
      showToast(res.has_alert ? `Submergence alert detected on ${highway}` : `Corridor ${highway} verified clear`, res.has_alert ? 'warning' : 'success');
    } catch (e) {
      showToast(e.message || 'Corridor check failed', 'error');
    } finally {
      setIsVerifying(false);
    }
  };
  return (
    <>
      {/* ── HERO SECTION ─────────────────────────────────── */}
      <section className="relative radar-grid-bg pt-8 pb-16 px-6 border-b border-outline-variant/30" id="advisory-map">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

          {/* LEFT: Command Intelligence Briefing */}
          <div className="lg:col-span-6 space-y-6">
            {/* Live Status Badge */}
            <div className="inline-flex items-center gap-2.5 px-3 py-1.5 rounded border border-primary-container/40 bg-surface-container-low backdrop-blur-md shadow-[0_0_15px_rgba(6,182,212,0.15)]">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-container"></span>
              </span>
              <span className="font-label-code text-label-code text-primary uppercase font-semibold tracking-wider">
                CYCLONE &amp; MONSOON ADVISORY: ACTIVE OVERPASS MONITORING
              </span>
            </div>

            <h1 className="font-display-hero text-headline-lg-mobile md:text-display-hero text-on-surface tracking-tight">
              Real-Time All-Weather Highway Intelligence During Cyclones &amp; Monsoons
            </h1>

            <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed">
              Powered by ESA Sentinel-1 C-Band SAR radar. Piercing dense monsoon cloud cover and torrential downpours
              at 5.405 GHz to detect millimeter-level highway submergence, culvert breaches, and coastal road washouts
              in near real-time across Gujarat.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <a href="#corridor-lookup" className="px-5 py-3 rounded bg-primary-container hover:bg-secondary text-surface-container-lowest font-headline-sm text-[16px] font-semibold flex items-center gap-2.5 shadow-[0_0_24px_rgba(6,182,212,0.4)] transition-all duration-150 transform hover:-translate-y-0.5">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>radar</span>
                <span>Launch SEOC Command Center</span>
              </a>
              <a href="#corridor-lookup" className="px-5 py-3 rounded border border-tertiary/60 bg-surface-container/60 hover:bg-tertiary/10 text-tertiary font-headline-sm text-[16px] font-medium flex items-center gap-2 transition-all duration-150">
                <span className="material-symbols-outlined">search</span>
                <span>Check Public Highway Status</span>
              </a>
            </div>

            <div className="pt-4 border-t border-outline-variant/30 flex flex-wrap gap-4 text-on-surface-variant font-label-code text-label-code">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-sm">satellite_alt</span>
                <span>ISRO / BISAG-N Telemetry Node</span>
              </div>
              <div className="text-outline">•</div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-sm">timelapse</span>
                <span>Revisit Frequency: 6–12 Hours</span>
              </div>
              <div className="text-outline">•</div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-tertiary text-sm">verified</span>
                <span>Submergence Accuracy: 98.4%</span>
              </div>
            </div>
          </div>

          {/* RIGHT: Tactical Radar HUD */}
          <div className="lg:col-span-6">
            <div className="hud-reticle rounded-xl border border-primary/30 bg-surface-container-lowest/80 backdrop-blur-xl p-5 shadow-[0_0_35px_rgba(6,182,212,0.18)] relative overflow-hidden">
              {/* HUD Header */}
              <div className="flex justify-between items-center border-b border-outline-variant/40 pb-3 mb-4 font-label-code text-label-code">
                <div className="flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined text-sm animate-spin" style={{ animationDuration: '9s' }}>autorenew</span>
                  <span>SYNCHRONIZED FEED // GUJARAT COASTAL CORRIDORS</span>
                </div>
                <div className="text-outline text-right">
                  POLARIZATION: <span className="text-on-surface font-semibold">VV + VH (C-BAND)</span>
                </div>
              </div>

              {/* Radar Map */}
              <div className="relative w-full h-[380px] rounded-lg bg-surface-container-lowest border border-outline-variant/30 overflow-hidden flex items-center justify-center">
                {/* Concentric rings */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                  <div className="w-24 h-24 rounded-full border border-primary absolute"></div>
                  <div className="w-48 h-48 rounded-full border border-primary absolute"></div>
                  <div className="w-72 h-72 rounded-full border border-primary absolute"></div>
                  <div className="w-96 h-96 rounded-full border border-primary absolute"></div>
                  <div className="absolute w-full h-[1px] bg-primary"></div>
                  <div className="absolute h-full w-[1px] bg-primary"></div>
                </div>
                {/* Sweep beam */}
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center animate-radar-sweep">
                  <div className="w-1/2 h-1/2 origin-bottom-right" style={{ background: 'conic-gradient(from 0deg at 100% 100%, rgba(76,215,246,0.35) 0deg, rgba(76,215,246,0) 60deg)' }}></div>
                </div>

                {/* SVG Gujarat map */}
                <svg className="absolute inset-0 w-full h-full p-4 pointer-events-none" viewBox="0 0 500 360" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M 60,80 Q 120,70 180,85 T 260,110 Q 280,140 240,165 Q 180,180 130,220 T 180,290 Q 230,300 270,270 Q 300,240 310,180 T 360,150 Q 390,200 400,280 T 430,340" stroke="rgba(148,163,184,0.3)" strokeWidth="1.5" strokeDasharray="4 2" />
                  <path d="M 280,115 L 295,160 L 310,210 L 330,260" stroke="#10B981" strokeWidth="3" strokeLinecap="round" filter="drop-shadow(0 0 4px #10B981)" />
                  <path d="M 295,160 L 370,175 L 420,270" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
                  <path d="M 125,185 L 140,215 L 155,245" stroke="#F59E0B" strokeWidth="3" strokeLinecap="round" />
                  <path d="M 140,215 L 148,230" stroke="#EF4444" strokeWidth="5" strokeDasharray="2 4" strokeLinecap="round" filter="drop-shadow(0 0 6px #EF4444)" className="animate-pulse" />
                  <circle cx="125" cy="185" r="4" fill="#06B6D4" />
                  <circle cx="140" cy="215" r="5" fill="#EF4444" className="animate-ping" />
                  <circle cx="140" cy="215" r="4" fill="#EF4444" />
                  <circle cx="155" cy="245" r="4" fill="#06B6D4" />
                  <circle cx="280" cy="115" r="4" fill="#10B981" />
                  <circle cx="310" cy="210" r="4" fill="#10B981" />
                  <circle cx="420" cy="270" r="4" fill="#10B981" />
                  <line x1="80" y1="10" x2="400" y2="350" stroke="rgba(76,215,246,0.4)" strokeWidth="1" strokeDasharray="6 4" />
                </svg>

                {/* Satellite tag */}
                <div className="absolute top-6 left-12 flex items-center gap-2 bg-surface-container-high/90 border border-primary/40 rounded px-2.5 py-1 text-[11px] font-label-code text-primary shadow-lg backdrop-blur-md">
                  <span className="material-symbols-outlined text-sm animate-pulse">satellite_alt</span>
                  <span>SENTINEL-1A • ALTITUDE: 693 KM</span>
                </div>

                {/* Alert callout */}
                <div className="absolute bottom-6 left-6 max-w-xs bg-surface-container-lowest/95 border-l-4 border-l-error border border-outline-variant/50 rounded p-3 shadow-[0_0_20px_rgba(239,68,68,0.25)] backdrop-blur-md">
                  <div className="flex items-center justify-between text-[11px] font-label-code mb-1">
                    <span className="text-error font-bold flex items-center gap-1">
                      <span className="material-symbols-outlined text-xs">warning</span>
                      SUBMERGENCE DETECTED
                    </span>
                    <span className="text-outline">12m AGO</span>
                  </div>
                  <div className="font-headline-sm text-xs font-semibold text-on-surface">GJ-SH-25 Porbandar – Dwarka</div>
                  <div className="font-label-code text-[11px] text-on-surface-variant mt-0.5">
                    Ch. 44+200 (Miyani Causeway) • <span className="text-error font-semibold">Depth: +32cm</span>
                  </div>
                  <div className="mt-2 text-[10px] font-label-code text-tertiary flex items-center gap-1">
                    <span className="material-symbols-outlined text-[12px]">turn_sharp_right</span>
                    DIVERSION: SH-27 via Ranavav Clear
                  </div>
                </div>

                {/* Coordinates */}
                <div className="absolute bottom-6 right-6 text-right font-label-code text-[11px] bg-surface-container-high/80 px-2.5 py-1.5 rounded border border-outline-variant/30">
                  <div className="text-primary font-semibold">21.6264° N, 69.6053° E</div>
                  <div className="text-outline text-[10px]">SAR COHERENCE: 0.94 • 5.405 GHz</div>
                </div>
              </div>

              {/* Bottom metrics bar */}
              <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-outline-variant/30 font-label-code text-center">
                {[
                  { label: 'LAST SAR OVERPASS', value: '14m 22s AGO', color: 'text-primary' },
                  { label: 'MONITORED BRIDGES', value: '1,482 STRUCTURES', color: 'text-on-surface' },
                  { label: 'COASTAL STORM SURGE', value: 'NOMINAL (+0.3M)', color: 'text-tertiary' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-surface-container-low p-2 rounded border border-outline-variant/20">
                    <div className="text-[10px] text-outline">{label}</div>
                    <div className={`text-sm font-bold ${color} mt-0.5`}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4 METRIC CARDS ───────────────────────────────── */}
      <section className="py-12 px-6 max-w-7xl mx-auto" id="telemetry-alerts">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              icon: 'add_road', tag: 'STATEWIDE', tagColor: 'primary',
              metric: '318+', title: 'State Highways Monitored',
              desc: 'Total 18,400+ km under continuous radar mesh surveillance synchronized with BISAG-N geosystems.',
            },
            {
              icon: 'speed', tag: 'RAPID-PIPELINE', tagColor: 'tertiary',
              metric: '<15 Min', title: 'Post-Overpass Processing',
              desc: 'Automated interferometric coherence (InSAR) and backscatter amplitude change detection in near real-time.',
            },
            {
              icon: 'cyclone', tag: 'ALL-WEATHER', tagColor: 'primary',
              metric: '100%', title: 'Cloud-Penetrating Radar',
              desc: 'Active microwave remote sensing impervious to cyclone rainbands, heavy fog, and pitch-black nights.',
            },
            {
              icon: 'cell_tower', tag: 'AUTO-DISPATCH', tagColor: 'secondary',
              metric: '±180s', title: 'Automated Chainage Alerts',
              desc: 'Instant alerts routed via SMS and digital VHF to R&B Executive Engineers, GSRTC depots, and police control.',
            },
          ].map(({ icon, tag, tagColor, metric, title, desc }) => (
            <div key={title} className="hud-reticle p-5 rounded-lg bg-surface-container-low border border-outline-variant/30 hover:border-primary/50 transition-all duration-200">
              <div className="flex items-center justify-between mb-3">
                <span className={`w-9 h-9 rounded bg-surface-container-high flex items-center justify-center text-${tagColor}`}>
                  <span className="material-symbols-outlined">{icon}</span>
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-label-code bg-${tagColor}/10 text-${tagColor} border border-${tagColor}/30`}>
                  {tag}
                </span>
              </div>
              <div className="font-telemetry-metric text-telemetry-metric text-on-surface">{metric}</div>
              <div className="font-headline-sm text-sm font-semibold text-on-surface mt-1">{title}</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-2">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CORRIDOR LOOKUP ───────────────────────────────── */}
      <section className="py-12 px-6 bg-surface-container-lowest border-y border-outline-variant/30" id="corridor-lookup">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
            <div>
              <div className="flex items-center gap-2 text-primary font-label-code text-label-code mb-2">
                <span className="material-symbols-outlined text-sm">route</span>
                <span>PUBLIC SAFETY NAVIGATION PROTOCOL • રાજ્ય ધોરીમાર્ગ સલામતી પોર્ટલ</span>
              </div>
              <h2 className="font-display-hero text-headline-lg text-on-surface">Verify Highway Corridor Safety Status</h2>
              <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl mt-1">
                Engineered for Gujarat citizens, freight logistics operators, and GSRTC intercity bus drivers to inspect real-time road conditions before departure.
              </p>
            </div>
            <div className="font-label-code text-xs text-outline bg-surface-container-low px-3 py-2 rounded border border-outline-variant/20 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-tertiary"></span>
              <span>LIVE RADAR SYNCHRONIZATION: 100% OPERATIONAL</span>
            </div>
          </div>

          {/* Search Box */}
          <div className="bg-surface-container-low border border-outline-variant/40 rounded-xl p-6 shadow-xl relative overflow-hidden hud-reticle">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
              <div className="md:col-span-3 space-y-1.5">
                <label className="font-label-code text-label-code text-on-surface-variant flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-primary text-xs">trip_origin</span>
                  <span>Origin District (ઉદ્ગમ જિલ્લો)</span>
                </label>
                <select 
                  value={origin}
                  onChange={e => setOrigin(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded text-on-surface font-body-md text-body-md px-3.5 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none">
                  <option value="Jamnagar">Jamnagar (જામનગર)</option>
                  <option value="Porbandar">Porbandar (પોરબંદર)</option>
                  <option value="Devbhumi Dwarka">Devbhumi Dwarka (દેવભૂમિ દ્વારકા)</option>
                  <option value="Kutch">Kutch (કચ્છ)</option>
                  <option value="Ahmedabad">Ahmedabad (અમદાવાદ)</option>
                </select>
              </div>
              <div className="md:col-span-3 space-y-1.5">
                <label className="font-label-code text-label-code text-on-surface-variant flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-xs">location_on</span>
                  <span>Destination District (ગંતવ્ય જિલ્લો)</span>
                </label>
                <select 
                  value={destination}
                  onChange={e => setDestination(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded text-on-surface font-body-md text-body-md px-3.5 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none">
                  <option value="Junagadh">Junagadh (જૂનાગઢ)</option>
                  <option value="Porbandar">Porbandar (પોરબંદર)</option>
                  <option value="Gir Somnath">Gir Somnath (ગીર સોમનાથ)</option>
                </select>
              </div>
              <div className="md:col-span-3 space-y-1.5">
                <label className="font-label-code text-label-code text-on-surface-variant flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-outline text-xs">signpost</span>
                  <span>Highway / Route Code (વૈકલ્પિક)</span>
                </label>
                <input 
                  value={highway}
                  onChange={e => setHighway(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded text-on-surface font-label-code text-body-md px-3.5 py-2.5 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none" placeholder="e.g. GJ-SH-25 or NH-51" type="text" />
              </div>
              <div className="md:col-span-3">
                <button 
                  onClick={handleVerifyCorridor}
                  disabled={isVerifying}
                  className="w-full bg-primary hover:bg-secondary text-surface-container-lowest font-headline-sm text-body-md font-semibold py-2.5 px-4 rounded flex items-center justify-center gap-2 shadow-[0_0_18px_rgba(76,215,246,0.35)] transition-all cursor-pointer disabled:opacity-50">
                  <span className="material-symbols-outlined">satellite_alt</span>
                  <span>{isVerifying ? 'Verifying Radar...' : 'Verify Safe Corridor'}</span>
                </button>
              </div>
            </div>

            {/* Result Card */}
            <div className="mt-6 pt-6 border-t border-outline-variant/30">
              <div className="bg-surface-container rounded-lg border border-outline-variant/50 p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 rounded font-label-code text-xs font-bold border flex items-center gap-1.5 ${corridorResult.has_alert ? 'bg-error-container text-on-error-container border-error/40' : 'bg-tertiary/20 text-tertiary border-tertiary/40'}`}>
                      <span className="material-symbols-outlined text-sm">{corridorResult.has_alert ? 'flood' : 'check_circle'}</span>
                      {corridorResult.status}
                    </span>
                    <span className="font-headline-md text-headline-sm font-semibold text-on-surface">{corridorResult.highway}</span>
                  </div>
                  <div className="font-label-code text-xs text-on-surface-variant flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-primary text-sm">update</span>
                    <span>{corridorResult.observed_at}</span>
                  </div>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center bg-surface-container-lowest/70 p-4 rounded border border-outline-variant/30">
                  <div className="lg:col-span-7 space-y-1">
                    <div className={`font-label-code text-xs font-medium flex items-center gap-1.5 ${corridorResult.has_alert ? 'text-error' : 'text-tertiary'}`}>
                      <span className="material-symbols-outlined text-sm">{corridorResult.has_alert ? 'warning' : 'verified'}</span>
                      <span>{corridorResult.chainage_span}</span>
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">
                      {corridorResult.depth_text}
                    </p>
                  </div>
                  <div className="lg:col-span-5 bg-surface-container-high/60 p-3 rounded border border-tertiary/30">
                    <div className="flex items-center gap-2 text-tertiary font-label-code text-xs font-semibold mb-1">
                      <span className="material-symbols-outlined text-sm">alt_route</span>
                      {corridorResult.has_alert ? 'APPROVED R&B SAFE DETOUR ROUTE' : 'RECOMMENDED TRANSIT CORRIDOR'}
                    </div>
                    <div className="text-on-surface font-body-sm text-xs">{corridorResult.detour_route}</div>
                    <div className="text-tertiary text-[11px] font-label-code mt-0.5">{corridorResult.detour_status}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── DISTRICT BULLETINS ────────────────────────────── */}
      <section className="py-14 px-6 max-w-7xl mx-auto" id="district-bulletins">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-3 mb-8">
          <div>
            <div className="flex items-center gap-2 text-primary font-label-code text-label-code mb-1">
              <span className="material-symbols-outlined text-sm">campaign</span>
              <span>DISTRICT ROAD &amp; HIGHWAY BULLETIN • જિલ્લાવાર અદ્યતન સ્થિતિ</span>
            </div>
            <h2 className="font-display-hero text-headline-lg text-on-surface">Monitored Coastal &amp; Riverine Corridors</h2>
          </div>
          <div className="font-label-code text-xs text-outline">UPDATED VIA AUTOMATED SENTINEL-1 INGESTION (POSTGRESQL)</div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(corridors.length > 0 ? corridors : [
            {
              district: 'DISTRICT: PORBANDAR & DWARKA', title: 'Saurashtra West Coast',
              status: 'ACTIVE WASHOUT RISK', statusColor: 'error',
              routes: [
                { name: 'GJ-SH-25 (Miyani Creek)', val: 'Submerged (28-32cm)', color: 'error' },
                { name: 'NH-51 Dwarka Coastal',     val: 'Clear • Watch active', color: 'tertiary' },
                { name: 'SH-27 Ranavav Detour',     val: 'High Navigability',   color: 'tertiary' },
              ],
              coherence: '0.76 (Unstable)',
            },
            {
              district: 'DISTRICT: VALSAD & NAVSARI', title: 'South Gujarat Arteries',
              status: 'ADVISORY MONITORING', statusColor: 'primary',
              routes: [
                { name: 'Auranga River Low-Bridge', val: 'Water Level +1.1m (Safe)', color: 'primary' },
                { name: 'NH-48 Vapi – Valsad',      val: 'Clear (No Ponding)',       color: 'tertiary' },
                { name: 'Daman Ganga Overpass',      val: 'Nominal Flow',             color: 'tertiary' },
              ],
              coherence: '0.94 (Stable)',
            },
            {
              district: 'DISTRICT: KUTCH & MORBI', title: 'Northern Highway Network',
              status: 'NORMAL CORRIDORS', statusColor: 'tertiary',
              routes: [
                { name: 'NH-41 Samakhiali – Gandhidham', val: 'Optimal Speed',         color: 'tertiary' },
                { name: 'GJ-SH-45 Khavda – Bhuj',        val: 'All Dry / Passable',    color: 'tertiary' },
                { name: 'Surajbari Creek Bridges',        val: 'Structural Soundness OK', color: 'tertiary' },
              ],
              coherence: '0.99 (Optimal)',
            },
          ]).map((c) => (
            <div key={c.title} className="hud-reticle bg-surface-container-low border border-outline-variant/40 rounded-xl p-5 shadow-lg relative">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="text-xs font-label-code text-outline">{c.district}</span>
                  <h3 className="font-headline-sm text-headline-sm text-on-surface mt-0.5">{c.title}</h3>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-label-code bg-${c.statusColor || 'primary'}/10 text-${c.statusColor || 'primary'} border border-${c.statusColor || 'primary'}/30 flex items-center gap-1`}>
                  <span className={`w-1.5 h-1.5 rounded-full bg-${c.statusColor || 'primary'} animate-ping`}></span>
                  {c.status}
                </span>
              </div>
              <div className="space-y-2.5 my-4">
                {(c.routes || []).map(({ name, val, color }) => (
                  <div key={name} className="flex justify-between text-xs font-label-code border-b border-outline-variant/20 pb-1.5">
                    <span className="text-on-surface-variant">{name}</span>
                    <span className={`text-${color || 'primary'} font-semibold truncate max-w-[200px]`}>{val}</span>
                  </div>
                ))}
              </div>
              <div className="text-[11px] font-label-code text-outline flex items-center justify-between pt-2">
                <span>InSAR Coherence: {c.coherence || (c.valid_pct ? `${c.valid_pct / 100} (Computed)` : '0.94 (Stable)')}</span>
                <button
                  onClick={() => {
                    const distClean = (c.title || c.district || '').replace('DISTRICT: ', '').replace(' Corridor', '').trim();
                    navigate(`/dashboard?district=${encodeURIComponent(distClean)}`);
                    showToast(`Navigating to GIS vector map for ${distClean}`, 'info');
                  }}
                  className="text-primary hover:underline cursor-pointer flex items-center gap-1 bg-transparent border-none p-0 text-[11px] font-label-code"
                >
                  View Map Vector →
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW SAR WORKS ────────────────────────────────── */}
      <section className="py-14 px-6 bg-surface-container-lowest/60 border-t border-outline-variant/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="font-label-code text-xs text-primary uppercase tracking-widest px-3 py-1 rounded bg-primary/10 border border-primary/30">
              MICROWAVE REMOTE SENSING DEEP-DIVE
            </span>
            <h2 className="font-display-hero text-headline-lg text-on-surface mt-3">
              How Synthetic Aperture Radar Detects Submergence Through Cyclone Storms
            </h2>
            <p className="font-body-md text-body-md text-on-surface-variant mt-2">
              Unlike standard optical satellites blinded by torrential rainclouds, SAR emits pulsed microwaves that slice through weather systems day or night.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01 // EMISSION & PENETRATION', icon: 'satellite', color: 'primary', title: '5.405 GHz Microwave Pulses', desc: 'C-Band radar waves possess a 5.6 cm wavelength, unaffected by tropospheric moisture, dense cyclone precipitation bands, or cloud layers.' },
              { step: '02 // SPECULAR REFLECTION', icon: 'water', color: 'tertiary', title: 'Specular Smooth-Water Bounce', desc: 'Dry asphalt highway surfaces scatter radar signals back to the sensor. Water-submerged roadbeds reflect signals away like a mirror, producing an immediate drop in backscatter.' },
              { step: '03 // REAL-TIME GIS CONFLATION', icon: 'notification_important', color: 'secondary', title: 'Edge Automated Alerts', desc: 'BISAG-N edge servers overlay radar masks against Gujarat\'s digital highway chainage vector database, instantly identifying exact culvert kilometre marks.' },
            ].map(({ step, icon, color, title, desc }) => (
              <div key={step} className="p-6 rounded-lg bg-surface-container-low border border-outline-variant/30 space-y-3">
                <div className={`font-label-code text-${color} text-xs`}>{step}</div>
                <div className={`w-12 h-12 rounded bg-surface-container-high flex items-center justify-center text-${color}`}>
                  <span className="material-symbols-outlined text-2xl">{icon}</span>
                </div>
                <h3 className="font-headline-sm text-lg text-on-surface">{title}</h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── DISASTER PROTOCOLS ────────────────────────────── */}
      <section className="py-12 px-6 max-w-7xl mx-auto" id="disaster-protocols">
        <div className="rounded-2xl border border-primary/30 bg-surface-container-low p-8 relative overflow-hidden hud-reticle">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-3">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-error-container/20 text-error font-label-code text-xs border border-error-container/40">
                <span className="material-symbols-outlined text-sm">support_agent</span>
                24/7 CITIZEN &amp; COMMUTER EMERGENCY TELEMETRY DESK
              </div>
              <h2 className="font-display-hero text-headline-lg text-on-surface">Trapped or Facing Severe Road Inundation?</h2>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Contact the Gujarat State Disaster Management Authority (GSDMA) State Emergency Operation Centre. All SAR-Drishti incident reports are georeferenced directly with local SDRF and R&amp;B rapid repair units.
              </p>
              <div className="flex flex-wrap gap-4 pt-2 font-label-code text-sm">
                <div className="text-on-surface">State SEOC: <strong className="text-primary">1070</strong></div>
                <div className="text-outline">•</div>
                <div className="text-on-surface">District Helpline: <strong className="text-primary">1077</strong></div>
                <div className="text-outline">•</div>
                <div className="text-on-surface">R&amp;B Highway Cell: <strong className="text-tertiary">1800-233-0101</strong></div>
              </div>
            </div>
            <div className="lg:col-span-4 flex flex-col gap-3">
              <a href="tel:1077" className="w-full py-3.5 px-6 rounded bg-error hover:bg-error-container text-on-error font-headline-sm text-center font-bold flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(239,68,68,0.4)] transition-all">
                <span className="material-symbols-outlined">call</span>
                <span>Dial Emergency: 1077</span>
              </a>
              <button
                onClick={async () => {
                  try {
                    const res = await fetch("http://127.0.0.1:8000/api/v1/bulletins/1.pdf");
                    if (!res.ok) { window.location.href = "/bulletin"; return; }
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "Gujarat_State_Evacuation_Map.pdf";
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                  } catch (e) {
                    window.location.href = "/bulletin";
                  }
                }}
                className="w-full py-3 px-6 rounded border border-primary/50 bg-surface-container hover:bg-surface-container-high text-primary font-label-code text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <span className="material-symbols-outlined text-sm">download_for_offline</span>
                Download Offline State Evacuation Map
              </button>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
