// PAGE 7: State Highway Submergence & Chainage Registry (Gujarat Live Telemetry)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function ChainageRegistry() {
  const [district, setDistrict] = useState('');
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');

  // Fetch real Gujarat data from FastAPI
  const { data: rowsData, loading } = useApi(
    () => api(`/chainage-events?district=${district}&category=${category}`),
    [district, category]
  );

  const { data: districtsData } = useApi(() => api('/meta/districts'));

  const rows = (rowsData || []).filter(r => 
    !search || r.id.toLowerCase().includes(search.toLowerCase()) || r.name.toLowerCase().includes(search.toLowerCase())
  );

  const districts = districtsData || [];

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // STATE HIGHWAY SUBMERGENCE & CHAINAGE REGISTRY"
        subtitle="RADAR BREACH LOG & GUJARAT HIGHWAY NETWORK SENSING"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail />

        <main className="flex-1 flex flex-col bg-surface-container-lowest overflow-hidden select-none">
          {/* Sub Header Title */}
          <div className="bg-surface-container-low/90 border-b border-outline-variant px-4 py-2 flex flex-wrap items-center justify-between gap-2 shrink-0">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-1.5 py-0.5 rounded bg-error/15 border border-error/40 text-error text-[10px] font-mono font-bold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping"></span>
                  SURVEILLANCE WATCH: LEVEL-4
                </span>
                <span className="text-on-surface-variant font-mono text-[11px]">// ROADS &amp; BUILDINGS DEPT, GUJARAT</span>
              </div>
              <h1 className="text-base font-bold text-on-surface tracking-tight mt-0.5">
                GUJARAT STATE HIGHWAY SUBMERGENCE &amp; CHAINAGE REGISTRY
              </h1>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="text-right">
                <div className="text-[10px] text-on-surface-variant">SAR POLARIZATION PASS</div>
                <div className="text-primary font-bold">VV + VH DUAL-POL</div>
              </div>
              <div className="h-6 w-px bg-outline-variant"></div>
              <div className="text-right">
                <div className="text-[10px] text-on-surface-variant">HYDRO RUNTIME</div>
                <div className="text-tertiary font-bold">COUPLED 2D HYDRO-DYNAMIC</div>
              </div>
            </div>
          </div>

          {/* 5 KPI Cards */}
          <section className="grid grid-cols-2 md:grid-cols-5 border-b border-outline-variant bg-surface-container-low shrink-0 divide-x divide-outline-variant/60">
            <div className="p-3">
              <span className="text-[10px] font-mono uppercase text-on-surface-variant">AFFECTED CORRIDORS</span>
              <div className="text-xl font-mono font-bold text-on-surface mt-1">{rows.length}</div>
              <div className="text-[10px] text-primary mt-0.5">SH: 3 | MDR: 1 Active</div>
            </div>
            <div className="p-3">
              <span className="text-[10px] font-mono uppercase text-on-surface-variant">ACTIVE OVERTOPPING</span>
              <div className="text-xl font-mono font-bold text-secondary mt-1">6,400 m</div>
              <div className="text-[10px] text-secondary mt-0.5">4 Critical Sectors</div>
            </div>
            <div className="p-3 bg-error/5">
              <span className="text-[10px] font-mono uppercase text-error font-bold">EMBANKMENT WASHOUT</span>
              <div className="text-xl font-mono font-bold text-error mt-1">1 Breach</div>
              <div className="text-[10px] text-error font-bold mt-0.5">Structural Hazard</div>
            </div>
            <div className="p-3">
              <span className="text-[10px] font-mono uppercase text-on-surface-variant">R&amp;B MACHINERY</span>
              <div className="text-xl font-mono font-bold text-tertiary mt-1">24 Units</div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">12 JCBs · 8 Tippers</div>
            </div>
            <div className="p-3">
              <span className="text-[10px] font-mono uppercase text-on-surface-variant">SAR ENGINE LOCK</span>
              <div className="text-sm font-mono font-bold text-primary mt-1">OTSU ADAPTIVE</div>
              <div className="text-[10px] text-tertiary mt-0.5">Bimodal Lock: 99.2%</div>
            </div>
          </section>

          {/* Toolbar */}
          <section className="p-2.5 bg-surface border-b border-outline-variant shrink-0 flex flex-wrap gap-2 items-center justify-between">
            <div className="flex flex-wrap items-center gap-2 flex-1">
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant rounded px-2.5 py-1 text-xs font-mono text-on-surface placeholder:text-outline w-64 focus:outline-none focus:border-primary"
                placeholder="Search Highway ID or Corridor..."
              />
              <select
                value={district}
                onChange={e => setDistrict(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant rounded px-2 py-1 text-xs font-mono text-on-surface"
              >
                <option value="">District: All Gujarat Districts</option>
                {districts.map(d => (
                  <option key={d.id} value={d.name}>{d.name}</option>
                ))}
              </select>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="bg-surface-container-lowest border border-outline-variant rounded px-2 py-1 text-xs font-mono text-on-surface"
              >
                <option value="">Risk: All Categories</option>
                <option value="Carriageway Overtopping">Carriageway Overtopping</option>
                <option value="Embankment Washout/Breach">Embankment Washout</option>
                <option value="Bridge Abutment High-Risk">Bridge Abutment High-Risk</option>
                <option value="Roadside Water Only - Passable">Roadside Water Only - Passable</option>
              </select>
            </div>
            <div className="flex items-center gap-1.5">
              <button 
                onClick={() => {
                  const token = sessionStorage.getItem('sd_token') || '';
                  window.open(`http://127.0.0.1:8000/api/v1/chainage-events/export.csv?token=${token}&district=${encodeURIComponent(district)}&category=${encodeURIComponent(category)}`, '_blank');
                  showToast('Exporting verified chainage telemetry to CSV...', 'info');
                }}
                className="px-2.5 py-1 border border-outline-variant bg-surface-container hover:bg-surface-container-high text-xs font-mono rounded"
              >
                Export CSV
              </button>
            </div>
          </section>

          {/* Table */}
          <div className="flex-1 overflow-auto bg-surface-container-lowest">
            {loading ? (
              <div className="p-8 text-center text-primary font-mono text-sm">
                SYNCHRONIZING SENTINEL-1 SAR PASS DATA...
              </div>
            ) : (
              <table className="w-full border-collapse text-left font-mono text-xs">
                <thead className="sticky top-0 bg-surface-container-low border-b border-outline-variant z-10 text-[11px] text-on-surface-variant uppercase">
                  <tr className="divide-x divide-outline-variant/40">
                    <th className="p-2 w-8 text-center"><input type="checkbox" className="rounded" /></th>
                    <th className="p-2">HIGHWAY ID &amp; CLASS</th>
                    <th className="p-2">DISTRICT / TALUKA</th>
                    <th className="p-2">AFFECTED CHAINAGE</th>
                    <th className="p-2">SUBMERGED LENGTH</th>
                    <th className="p-2">DEM WATER DEPTH</th>
                    <th className="p-2">CATEGORY</th>
                    <th className="p-2">CONFIDENCE</th>
                    <th className="p-2 text-right">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/40">
                  {rows.map((r) => (
                    <tr key={r.id} className="hover:bg-surface-container/50 transition-colors">
                      <td className="p-2 text-center"><input type="checkbox" className="rounded" /></td>
                      <td className="p-2">
                        <div className="flex items-center gap-2">
                          {r.pulse ? (
                            <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>
                          ) : (
                            <span className={`w-2 h-2 rounded-full bg-${r.catColor}`}></span>
                          )}
                          <div>
                            <div className="font-bold text-on-surface flex items-center gap-1">
                              <span>{r.id}</span>
                              <span className="px-1 text-[9px] bg-surface-container-high rounded text-primary border border-primary/20">{r.type}</span>
                            </div>
                            <div className="text-[10px] text-on-surface-variant truncate max-w-[150px]">{r.name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="p-2">
                        <div className="font-semibold text-on-surface">{r.dist}</div>
                        <div className="text-[10px] text-outline">{r.block}</div>
                      </td>
                      <td className="p-2">
                        <div className={`font-bold ${r.catColor === 'error' ? 'text-error' : 'text-on-surface'}`}>{r.chainage}</div>
                        <div className="text-[10px] text-outline">{r.flank}</div>
                      </td>
                      <td className="p-2">
                        <div className="font-bold text-on-surface">{r.len}</div>
                        <div className="w-24 bg-surface-container-highest h-1 rounded mt-1 overflow-hidden">
                          <div className={`bg-${r.catColor} h-full`} style={{ width: r.cwPct }}></div>
                        </div>
                      </td>
                      <td className="p-2">
                        <span className={`px-1.5 py-0.5 rounded font-bold text-[10px] bg-${r.catColor}/20 text-${r.catColor} border border-${r.catColor}/40`}>
                          {r.depth}
                        </span>
                      </td>
                      <td className="p-2">
                        <span className={`text-[10px] font-bold text-${r.catColor}`}>{r.cat}</span>
                      </td>
                      <td className="p-2">
                        <div className="font-bold text-on-surface">{r.conf}</div>
                        <div className="text-[9px] text-outline">{r.db}</div>
                      </td>
                      <td className="p-2 text-right">
                        <button className="px-2 py-0.5 bg-primary/20 text-primary border border-primary/40 rounded text-[10px] font-bold hover:bg-primary hover:text-surface-container-lowest transition-colors">
                          Assign R&amp;B
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Footer Pagination */}
          <footer className="bg-surface-container-low border-t border-outline-variant px-4 py-2 flex items-center justify-between font-mono text-xs text-on-surface-variant shrink-0">
            <div>Showing {rows.length} critical chainage segments in Gujarat</div>
            <div className="flex items-center gap-1">
              <button className="px-2 py-0.5 rounded bg-primary/20 text-primary font-bold border border-primary/40">1</button>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
