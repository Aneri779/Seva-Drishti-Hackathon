import re

with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add imports & state
import_block = """// PAGE 1: SAR-Drishti Home / Advisory Map
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function HomePage() {
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
  };"""

text = re.sub(
    r"// PAGE 1: SAR-Drishti Home / Advisory Map\s*import \{ Link \} from 'react-router-dom';\s*export default function HomePage\(\) \{",
    import_block,
    text
)

# 2. Replace Search Box
old_search_pattern = r'<select className="w-full bg-surface-container-lowest border border-outline-variant/40 rounded text-on-surface font-body-md text-body-md px-3\.5 py-2\.5 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none">\s*<option value="jamnagar">.*?<button className="w-full bg-primary hover:bg-secondary text-surface-container-lowest font-headline-sm text-body-md font-semibold py-2\.5 px-4 rounded flex items-center justify-center gap-2 shadow-\[0_0_18px_rgba\(76,215,246,0\.35\)\] transition-all">\s*<span className="material-symbols-outlined">satellite_alt</span>\s*<span>Verify Safe Corridor</span>\s*</button>'

new_search = """<select 
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
                </button>"""

text = re.sub(old_search_pattern, new_search, text, flags=re.DOTALL)

# 3. Replace Result card
old_result_pattern = r'\{\/\* Result Card \*\/\}\s*<div className="mt-6 pt-6 border-t border-outline-variant/30">.*?STATUS: ALL CLEAR • Radar Coherence: 0\.98 \(High Stability\)</div>\s*</div>\s*</div>\s*</div>\s*</div>'

new_result = """{/* Result Card */}
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
            </div>"""

text = re.sub(old_result_pattern, new_result, text, flags=re.DOTALL)

with open('d:/Seva_innovation/seva_first_hackathon/src/pages/HomePage.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("HomePage successfully patched via regex!")

