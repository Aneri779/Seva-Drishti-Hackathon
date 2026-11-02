// PAGE 10: SEOC // Automated District Flood Bulletin Generator (Live PostgreSQL Integration)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function BulletinGenerator() {
  const [district, setDistrict] = useState('Gir Somnath');
  const [signed, setSigned] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeBulletin, setActiveBulletin] = useState(null);
  const [language, setLanguage] = useState('en'); // 'en' or 'gu'

  const { data: districtsData } = useApi(() => api.get('/meta/districts'));
  const { data: bulletinsData, refetch } = useApi(() => api.get('/bulletins'));

  const districts = districtsData || [];
  const archives = bulletinsData || [];

  const activeDistrictObj = districts.find(d => d.name === (activeBulletin?.district || district));
  const displayDistrictName = language === 'gu' 
    ? (activeDistrictObj?.name_gu || activeDistrictObj?.name || district)
    : (activeDistrictObj?.name || district);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const res = await api.post('/bulletins', { district });
      setActiveBulletin(res);
      showToast(`Real Flood Bulletin generated for ${district} (SHA-256: ${res.sha256.substring(0, 8)}...)`, 'success');
      refetch();
    } catch (e) {
      showToast(e.message || 'Failed to generate bulletin', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSign = async () => {
    const targetId = activeBulletin?.id || (archives.length > 0 ? archives[0].id : null);
    if (!targetId) {
      showToast('Please generate or select a bulletin first', 'warning');
      return;
    }
    try {
      const res = await api.post(`/bulletins/${targetId}/sign`, {});
      setSigned(true);
      showToast(`PAdES Digital Signature Applied: Verified by ${res.signed_by}`, 'success');
      refetch();
    } catch (e) {
      showToast(e.message || 'Signature application failed', 'error');
    }
  };

  const handleDownload = async (id) => {
    try {
      const token = sessionStorage.getItem('sd_token') || '';
      const response = await fetch(`http://127.0.0.1:8000/api/v1/bulletins/${id}.pdf?token=${token}`);
      if (!response.ok) {
        throw new Error(`Download failed: HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Gujarat_Flood_Bulletin_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showToast('Official District Flood Bulletin downloaded successfully.', 'success');
    } catch (e) {
      showToast(e.message || 'Failed to download PDF', 'error');
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // SENTINEL-1 TELEMETRY"
        subtitle="AUTOMATED DISTRICT FLOOD BULLETIN GENERATOR // જિલ્લા પૂર બુલેટિન જનરેટર"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail compact={true} />

        <main className="flex-1 grid grid-cols-12 overflow-hidden bg-surface-container-lowest select-none">
          {/* LEFT: Config & Archive (col-5) */}
          <section className="col-span-12 xl:col-span-5 flex flex-col border-r border-outline-variant bg-surface overflow-y-auto p-4 space-y-4">
            <div className="flex items-center justify-between border-b border-outline-variant pb-2">
              <div>
                <h2 className="text-sm font-bold text-on-surface">BULLETIN DISPATCH ENGINE</h2>
                <p className="text-[10px] font-mono text-outline">R&amp;B DEPT STATE HIGHWAYS INUNDATION SURVEILLANCE</p>
              </div>
              <span className="px-2 py-0.5 rounded bg-error/20 border border-error text-error text-[10px] font-mono font-bold">
                URGENT // SEC-34
              </span>
            </div>

            {/* Target district & params */}
            <div className="p-3 rounded bg-surface-container border border-outline-variant space-y-3 font-mono text-xs">
              <div>
                <label className="text-[10px] text-outline block mb-1">TARGET DISTRICT JURISDICTION (GUJARAT)</label>
                <select
                  value={district}
                  onChange={e => setDistrict(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded p-2 text-on-surface text-xs focus:outline-none focus:border-primary"
                >
                  {districts.map(d => (
                    <option key={d.id} value={d.name}>{d.name} ({d.name_gu})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <label className="text-[10px] text-outline block mb-1">RADAR PASS</label>
                  <select className="w-full bg-surface-container-lowest border border-outline-variant rounded p-1.5 text-primary text-xs">
                    <option>PASS 142 ASCENDING (Current)</option>
                    <option>PASS 098 DESCENDING (-8h)</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-outline block mb-1">LANGUAGE</label>
                  <div className="grid grid-cols-2 gap-1 p-0.5 bg-surface-container-lowest border border-outline-variant rounded text-center">
                    <button 
                      onClick={() => setLanguage('en')}
                      className={`py-1 rounded text-[10px] font-bold transition-colors ${language === 'en' ? 'bg-primary text-surface-container-lowest' : 'text-on-surface-variant hover:text-on-surface'}`}
                    >
                      English
                    </button>
                    <button 
                      onClick={() => setLanguage('gu')}
                      className={`py-1 rounded text-[10px] font-bold transition-colors ${language === 'gu' ? 'bg-primary text-surface-container-lowest' : 'text-on-surface-variant hover:text-on-surface'}`}
                    >
                      ગુજરાતી
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full py-2 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint shadow active:scale-95 transition-all disabled:opacity-50"
            >
              {isGenerating ? 'GENERATING PDF REPORT...' : 'GENERATE OFFICIAL FLOOD BULLETIN'}
            </button>

            {/* Historical Archive from API */}
            <div className="flex-1 flex flex-col space-y-2 font-mono">
              <span className="text-[10px] text-outline uppercase font-bold tracking-wider">
                GENERATED BULLETINS ARCHIVE (POSTGRESQL)
              </span>
              <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
                {archives.length === 0 ? (
                  <div className="p-3 text-xs text-on-surface-variant font-mono text-center">No bulletins yet generated. Click Generate above.</div>
                ) : (
                  archives.map(b => (
                    <div
                      key={b.id}
                      onClick={() => setActiveBulletin(b)}
                      className={`p-2.5 rounded border transition-colors cursor-pointer text-xs ${
                        activeBulletin?.id === b.id ? 'bg-primary/10 border-primary' : 'bg-surface-container-lowest border-outline-variant/40 hover:border-outline'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-primary">{b.code || `#GUJ-BULLETIN-${b.id}`}</span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] ${b.status === 'signed' ? 'bg-green-500/20 text-green-400 border border-green-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'}`}>
                          {b.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-[11px] text-on-surface mt-1">{b.district} District Flood Inundation Report</div>
                      <div className="text-[9px] text-outline flex items-center justify-between mt-1">
                        <span>{b.meta}</span>
                        <span className="truncate max-w-[120px]">SHA: {b.sha256?.substring(0, 10)}...</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>

          {/* RIGHT: Live Preview & Sign (col-7) */}
          <section className="col-span-12 xl:col-span-7 flex flex-col bg-surface-container-lowest p-6 overflow-y-auto">
            <div className="max-w-2xl mx-auto w-full flex-1 flex flex-col justify-between bg-surface-container p-6 rounded-xl border border-outline-variant shadow-lg font-mono">
              <div>
                <div className="flex items-center justify-between border-b border-outline-variant/40 pb-4 mb-4">
                  <div>
                    <h3 className="font-bold text-base text-primary">
                      {language === 'gu' ? 'રાજ્ય આપાતકાલીન કામગીરી કેન્દ્ર (SEOC)' : 'STATE EMERGENCY OPERATION CENTRE'}
                    </h3>
                    <p className="text-xs text-on-surface-variant">
                      {language === 'gu' ? 'માર્ગ અને મકાન વિભાગ, ગુજરાત સરકાર' : 'ROADS & BUILDINGS DEPARTMENT, GUJARAT'}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-outline block">DIGITAL SHA-256 HASH</span>
                    <span className="text-[11px] font-bold text-green-400">
                      {activeBulletin?.sha256 ? `${activeBulletin.sha256.substring(0, 16)}...` : 'ba436318c307ca4f...'}
                    </span>
                  </div>
                </div>

                <div className="space-y-4 text-xs leading-relaxed">
                  <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/50">
                    <span className="font-bold text-on-surface">
                      {language === 'gu' ? 'લક્ષ્ય જિલ્લો / સેક્ટર: ' : 'Target Sector: '}
                    </span>
                    <span className="text-primary font-bold">
                      {displayDistrictName} {language === 'gu' ? 'દરિયાકાંઠા અને નદી બેસિન' : 'Coastal & River Basins'}
                    </span>
                  </div>

                  <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/50 space-y-2">
                    <div className="font-bold text-on-surface">
                      {language === 'gu' ? 'રાડાર પૂર નિરીક્ષણ (સેન્ટિનેલ-૧ SAR):' : 'Radar Inundation Observations (Sentinel-1 SAR):'}
                    </div>
                    {language === 'gu' ? (
                      <ul className="list-disc pl-5 space-y-1 text-on-surface-variant text-[11px]">
                        <li>નીચાણવાળા પુલ અને કોઝવે પર સ્પેક્યુલર બેકસ્કેટર ડ્રોપ જોવા મળ્યો (-12.8 dB થી -15.6 dB)</li>
                        <li>રાજ્ય ધોરીમાર્ગ GJ-SH-25 અને GJ-SH-41 પર પાણી ફરી વળવાની પુષ્ટિ થયેલ છે</li>
                        <li>કોપરનિકસ ૩૦ મીટર DEM મુજબ અંદાજિત પૂર ઊંડાઈ (+૦.૪૨ મીટર થી +૦.૬૨ મીટર)</li>
                      </ul>
                    ) : (
                      <ul className="list-disc pl-5 space-y-1 text-on-surface-variant text-[11px]">
                        <li>Specular backscatter drop detected across low-lying road culverts (-12.8 dB to -15.6 dB)</li>
                        <li>Water overtopping identified across state corridors GJ-SH-25 and GJ-SH-41</li>
                        <li>Estimated submergence depth computed using Copernicus 30 m DEM (+0.42m to +0.62m)</li>
                      </ul>
                    )}
                  </div>

                  <div className="p-3 bg-surface-container-lowest rounded border border-outline-variant/50 flex items-center justify-between">
                    <div>
                      <div className="text-[10px] text-outline">
                        {language === 'gu' ? 'ડિજિટલ પ્રમાણપત્ર સ્થિતિ' : 'PAdES CERTIFICATE STATUS'}
                      </div>
                      <div className="font-bold text-green-400">
                        {signed || activeBulletin?.status === 'signed' 
                          ? (language === 'gu' ? '✓ NIC વર્ગ-૩ ડિજિટલ સહી પ્રમાણિત' : '✓ NIC CLASS-3 DSC APPLIED')
                          : (language === 'gu' ? 'અધિકૃત સહી બાકી' : 'PENDING OFFICIAL SIGNATURE')}
                      </div>
                    </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDownload(activeBulletin?.id || (archives.length > 0 ? archives[0].id : null))}
                          className="px-3 py-1 bg-surface-container-high border border-outline-variant rounded hover:text-primary text-xs flex items-center gap-1 cursor-pointer"
                        >
                          <span className="material-symbols-outlined text-sm">download</span>
                          <span>Download PDF</span>
                        </button>
                      </div>
                  </div>
                </div>
              </div>

              <div className="pt-6 border-t border-outline-variant/40 flex items-center justify-between">
                <span className="text-[10px] text-outline">ISSUED UNDER GUJARAT DISASTER MANAGEMENT ACT</span>
                <button
                  onClick={handleSign}
                  disabled={signed || activeBulletin?.status === 'signed'}
                  className="px-6 py-2.5 bg-tertiary text-surface-container-lowest font-bold text-xs rounded hover:bg-tertiary-fixed disabled:opacity-50 transition shadow"
                >
                  {signed || activeBulletin?.status === 'signed' ? 'DIGITALLY SIGNED' : 'SIGN & DISPATCH BULLETIN'}
                </button>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
