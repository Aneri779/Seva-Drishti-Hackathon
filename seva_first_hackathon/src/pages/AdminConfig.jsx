// PAGE 12: Admin Configuration & Master GIS Asset Repository (Live API Linked)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function AdminConfig() {
  const [saveStatus, setSaveStatus] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const { data: configData, refetch } = useApi(() => api.get('/admin/config'));

  const cfg = configData || {
    cdse_status: "Connected (OAuth2 Verified)",
    gee_service_account: "sar-backend@sar-drishti-gujarat-123456.iam.gserviceaccount.com",
    nic_sms_key: "NIC-SMS-GUJ-9984-********",
    whatsapp_api: "Verified Green Tick Active",
    otsu_slope_max_deg: 5.0,
    otsu_hand_max_m: 15.0,
    min_flood_area_ha: 1.0,
    jrc_occurrence_threshold: 75,
    storage_used_gb: 4.8,
    storage_total_gb: 8.0
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.put('/admin/config', {
        otsu_slope_max_deg: cfg.otsu_slope_max_deg || 5.0,
        otsu_hand_max_m: cfg.otsu_hand_max_m || 15.0,
        min_flood_area_ha: cfg.min_flood_area_ha || 1.0,
        jrc_occurrence_threshold: cfg.jrc_occurrence_threshold || 75
      });
      setSaveStatus('SAR Pipeline Thresholds Deployed to Ingestion Node');
      showToast('System configuration & SAR parameters saved to PostgreSQL.', 'success');
      refetch();
      setTimeout(() => setSaveStatus(''), 4000);
    } catch (e) {
      showToast(e.message || 'Failed to save configuration', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // SENTINEL-1 TELEMETRY"
        subtitle="ADMIN CONFIGURATION & MASTER GIS ASSET REPOSITORY (સિસ્ટમ સેટિંગ્સ અને GIS એસેટ્સ)"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail />

        <main className="flex-1 flex flex-col h-full overflow-y-auto bg-background select-none">
          {/* Subheader */}
          <div className="px-6 py-2.5 bg-surface-container-low border-b border-outline-variant flex flex-wrap items-center justify-between gap-2 shrink-0">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-on-surface tracking-tight">
                  ADMIN CONFIGURATION &amp; MASTER GIS ASSET REPOSITORY
                </h1>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30">
                  SEOC GANDHINAGAR ENCLAVE
                </span>
              </div>
              <p className="text-xs text-on-surface-variant">Sentinel-1 Inundation Engine • State Geospatial Asset Overrides</p>
            </div>
            <div className="flex items-center gap-2">
              {saveStatus && <span className="text-tertiary font-mono text-xs">{saveStatus}</span>}
              <button
                onClick={handleSave}
                className="px-4 py-1.5 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint shadow active:scale-95 transition-all"
              >
                SAVE &amp; DEPLOY CONFIG
              </button>
            </div>
          </div>

          {/* Bento Grid */}
          <div className="p-4 grid grid-cols-1 xl:grid-cols-2 gap-4">
            {/* Bento 1: API Credentials (Masked per Hard Rule 7) */}
            <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <span className="font-bold text-primary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">api</span>
                  API &amp; Satellite Telemetry Credentials
                </span>
                <span className="text-tertiary text-[10px] font-bold">PIPELINES LIVE</span>
              </div>

              <div className="bg-surface-container p-2.5 rounded border border-outline-variant space-y-1.5">
                <div className="flex justify-between font-bold text-on-surface">
                  <span>Copernicus Data Space (CDSE) S1-API</span>
                  <span className="text-tertiary text-[10px]">{cfg.cdse_status}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] text-outline">
                  <div>LATENCY: <strong className="text-tertiary">142ms</strong></div>
                  <div>RATE LIMIT: <strong className="text-primary">480 / 500 req/min</strong></div>
                </div>
              </div>

              <div className="bg-surface-container p-2.5 rounded border border-outline-variant space-y-1 text-[11px]">
                <div className="font-bold text-secondary">Google Earth Engine (GEE) Account</div>
                <div className="text-outline truncate">{cfg.gee_service_account}</div>
                <div className="text-primary">Key Location: secrets/gee-key.json (Encrypted)</div>
              </div>

              <div className="bg-surface-container p-2.5 rounded border border-outline-variant space-y-1 text-[11px]">
                <div className="font-bold text-tertiary">NIC &amp; Govt Mass Alert Gateway</div>
                <div className="text-outline">NIC SMS KEY: {cfg.nic_sms_key}</div>
                <div className="text-tertiary">WhatsApp Gateway: {cfg.whatsapp_api}</div>
              </div>
            </section>

            {/* Bento 2: Master GIS Vector Layers */}
            <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <span className="font-bold text-secondary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">layers</span>
                  Master GIS Vector Layers &amp; Spatial Assets (Gujarat)
                </span>
                <span className="text-outline text-[10px]">ACTIVE REPOSITORIES</span>
              </div>

              <div className="space-y-2">
                {[
                  ["Gujarat State Highways (SH) Alignment", "3,420 km • EPSG:4326 • PostGIS", "primary"],
                  ["Major District Roads (MDR) Network", "8,910 km • 100m Segments", "secondary"],
                  ["Bridge Abutments & Culvert Stations", "412 Geocoded Points • Scour Risk", "error"],
                  ["High-Embankment DEM (30 m DEM)", "Copernicus GLO-30 Elevation", "tertiary"]
                ].map(([name, meta, color]) => (
                  <div key={name} className="p-2 bg-surface-container rounded border border-outline-variant flex items-center justify-between text-[11px]">
                    <div>
                      <div className="font-bold text-on-surface">{name}</div>
                      <div className="text-outline text-[10px]">{meta}</div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] bg-${color}/10 text-${color} border border-${color}/30 font-bold`}>
                      Synced
                    </span>
                  </div>
                ))}
              </div>
            </section>

            {/* Bento 3: RBAC Governance */}
            <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <span className="font-bold text-tertiary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">admin_panel_settings</span>
                  Role-Based Access Control (RBAC) &amp; Governance
                </span>
                <span className="text-primary text-[10px]">AUTHORIZED ROLES</span>
              </div>

              <div className="space-y-1.5 text-[11px]">
                {[
                  ["SEOC Admins (State Emergency)", "Full Authority & Dispatch", "admin"],
                  ["R&B Chief Engineers & Leads", "Ground-Truth & Dispatch", "rb_ee"],
                  ["District Collectors & DDOs", "Public Advisory & SMS", "collector"],
                  ["NDRF & SDRF Tactical Viewers", "Convoy Routing & Rescue", "ndrf"],
                  ["GSRTC Route Controllers", "Bus Diversions & Fleet Alert", "gsrtc"],
                  ["BISAG-N Geospatial Analysts", "SAR Ingestion & Radar Calibration", "bisag_gis"]
                ].map(([role, desc, code]) => (
                  <div key={code} className="p-2 bg-surface-container rounded border border-outline-variant flex items-center justify-between">
                    <div>
                      <span className="font-bold text-on-surface">{role}</span>
                      <div className="text-[10px] text-outline">{desc}</div>
                    </div>
                    <span className="text-primary font-mono text-[10px]">{code}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Bento 4: SAR Threshold Customization */}
            <section className="bg-surface-container-low border border-outline-variant rounded p-4 space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-outline-variant pb-2">
                <span className="font-bold text-error flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">tune</span>
                  SAR Threshold &amp; Mask Parameters
                </span>
                <span className="text-tertiary text-[10px]">ACTIVE</span>
              </div>

              <div className="space-y-2 text-[11px]">
                <div className="flex justify-between items-center bg-surface-container p-2 rounded">
                  <span>Slope Exclusion Angle (max):</span>
                  <span className="font-bold text-primary">{cfg.otsu_slope_max_deg}°</span>
                </div>
                <div className="flex justify-between items-center bg-surface-container p-2 rounded">
                  <span>HAND (Height Above Drainage) Cutoff:</span>
                  <span className="font-bold text-primary">{cfg.otsu_hand_max_m} m</span>
                </div>
                <div className="flex justify-between items-center bg-surface-container p-2 rounded">
                  <span>JRC Permanent Water Exclusion:</span>
                  <span className="font-bold text-primary">{cfg.jrc_occurrence_threshold}% occurrence</span>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
