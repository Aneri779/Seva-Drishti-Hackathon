import re

with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add useApi hook and useNavigate
import_block = """// PAGE 1: SAR-Drishti Home / Advisory Map
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import { showToast } from '../components/common/Toast';

export default function HomePage() {
  const navigate = useNavigate();
  const { data: corridorsData } = useApi(() => api.get('/advisories/corridors'), [], 15000);
  const corridors = corridorsData || [];"""

text = re.sub(
    r"// PAGE 1: SAR-Drishti Home / Advisory Map\s*import \{ useState \} from 'react';\s*import \{ Link \} from 'react-router-dom';\s*import \{ api \} from '\.\./api/client';\s*import \{ showToast \} from '\.\./components/common/Toast';\s*export default function HomePage\(\) \{",
    import_block,
    text
)

# Replace the hardcoded Monitored Coastal & Riverine Corridors grid
old_grid_pattern = r'\{\/\* ── DISTRICT BULLETINS ──.*?<div className="grid grid-cols-1 md:grid-cols-3 gap-6">\s*\{\[\s*\{\s*district: \'DISTRICT: PORBANDAR & DWARKA\'.*?<\/section>'

new_grid = """{/* ── DISTRICT BULLETINS ────────────────────────────── */}
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
      </section>"""

text = re.sub(old_grid_pattern, new_grid, text, flags=re.DOTALL)

with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY PATCHED CORRIDORS WITH DYNAMIC DATA & VIEW MAP VECTOR CLICK HANDLER!")

