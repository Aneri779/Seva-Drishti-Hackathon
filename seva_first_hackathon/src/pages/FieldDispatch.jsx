// PAGE 11: R&B Field Engineer & Machinery Dispatch Tracker (Live Kanban Linked)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function FieldDispatch() {
  const [reportSubmitted, setReportSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { data: tasksData, refetch } = useApi(() => api.get('/dispatch-tasks'));

  const tasks = tasksData || [];
  const hotspots = tasks.filter(t => t.column_state === 'hotspot');
  const dispatched = tasks.filter(t => t.column_state === 'dispatched');
  const cleared = tasks.filter(t => t.column_state === 'cleared');

  const handleDeploy = async (taskId) => {
    try {
      await api.patch(`/dispatch-tasks/${taskId}`, {
        column_state: 'dispatched',
        progress_pct: 25
      });
      showToast('Machinery unit deployed to hotspot location', 'success');
      refetch();
    } catch (e) {
      showToast(e.message || 'Failed to deploy machinery', 'error');
    }
  };

  const handleAdvanceProgress = async (taskId, currentPct) => {
    const nextPct = Math.min(100, currentPct + 25);
    const nextState = nextPct >= 100 ? 'cleared' : 'dispatched';
    try {
      await api.patch(`/dispatch-tasks/${taskId}`, {
        column_state: nextState,
        progress_pct: nextPct
      });
      showToast(`Task progress updated to ${nextPct}%`, 'success');
      refetch();
    } catch (e) {
      showToast(e.message || 'Failed to update progress', 'error');
    }
  };

  const handleFeedback = async () => {
    setIsSubmitting(true);
    try {
      // Find an active task or use the first task to attach the ground truth report
      const targetTask = tasks[0];
      if (targetTask) {
        await api.patch(`/dispatch-tasks/${targetTask.id}`, {
          verdict: 'CONFIRMED',
          field_report: {
            observed_depth_m: 0.38,
            delta_m: -0.04,
            otsu_offset_suggested: 0.2,
            verified: true,
            notes: 'True positive submergence verified against Sentinel-1 Otsu threshold.'
          }
        });
      }
      setReportSubmitted(true);
      showToast('Ground truth verification submitted & synced to PostgreSQL audit log.', 'success');
      refetch();
    } catch (e) {
      showToast(e.message || 'Ground truth submission failed', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // SENTINEL-1 TELEMETRY"
        subtitle="R&B RAPID ACTION FORCE // FIELD TRUTHING & REPAIR WORKSTATION (ક્ષેત્ર ચકાસણી અને મશીનરી ટ્રેકર)"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail />

        <main className="flex-1 flex flex-col xl:flex-row overflow-hidden bg-surface-container-lowest">
          {/* LEFT: Kanban (60%) */}
          <section className="w-full xl:w-[60%] flex flex-col border-r border-outline-variant overflow-hidden">
            <div className="px-4 py-2 border-b border-outline-variant bg-surface-container-low flex justify-between items-center text-xs font-mono shrink-0">
              <span className="font-bold text-on-surface uppercase">GROUND VERIFICATION &amp; MACHINERY DISPATCH</span>
              <span className="text-outline">DISTRICT: PORBANDAR &amp; GIR SOMNATH R&amp;B CIRCLE</span>
            </div>

            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-outline-variant overflow-y-auto">
              {/* Col 1: Hotspots */}
              <div className="p-3 space-y-2.5 overflow-y-auto">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-error font-bold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>
                    SAR HOTSPOTS
                  </span>
                  <span className="px-1.5 py-0.2 bg-error/20 text-error rounded text-[10px] font-bold">{hotspots.length} CRITICAL</span>
                </div>

                {hotspots.map((h) => (
                  <div key={h.id} className="bg-surface-container border border-error/40 rounded p-2.5 space-y-2 text-xs font-mono">
                    <div className="flex justify-between font-bold text-on-surface">
                      <span>{h.road}</span>
                      <span className="text-error text-[10px]">{h.cat}</span>
                    </div>
                    <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant text-[11px] space-y-0.5">
                      <div className="flex justify-between"><span>RADAR EST:</span> <span className="text-error font-bold">{h.depth}</span></div>
                      <div className="flex justify-between"><span>MACHINERY:</span> <span className="text-secondary">{h.machinery}</span></div>
                    </div>
                    <button
                      onClick={() => handleDeploy(h.id)}
                      className="w-full py-1 bg-primary text-surface-container-lowest font-bold rounded hover:bg-surface-tint"
                    >
                      Deploy Unit
                    </button>
                  </div>
                ))}
              </div>

              {/* Col 2: Dispatched */}
              <div className="p-3 space-y-2.5 overflow-y-auto">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-primary font-bold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-primary"></span>
                    MACHINERY DISPATCHED
                  </span>
                  <span className="px-1.5 py-0.2 bg-primary/20 text-primary rounded text-[10px] font-bold">{dispatched.length} ACTIVE</span>
                </div>

                {dispatched.map((d) => (
                  <div key={d.id} className="bg-surface-container border-2 border-primary rounded p-2.5 space-y-2 text-xs font-mono shadow">
                    <div className="font-bold text-primary">{d.road}</div>
                    <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant text-[11px] space-y-0.5">
                      <div className="font-bold text-on-surface">{d.machinery}</div>
                      <div className="text-outline">Lead: {d.assignee}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span>BREACH CONTAINMENT:</span>
                        <span className="text-tertiary font-bold">{d.progress_pct}% Completed</span>
                      </div>
                      <div className="w-full bg-surface-container-highest h-1.5 rounded overflow-hidden">
                        <div className="bg-tertiary h-full" style={{ width: `${d.progress_pct}%` }}></div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAdvanceProgress(d.id, d.progress_pct)}
                      className="w-full mt-2 py-0.5 bg-tertiary/20 text-tertiary border border-tertiary/40 text-[10px] font-bold rounded hover:bg-tertiary/30"
                    >
                      +25% Progress
                    </button>
                  </div>
                ))}
              </div>

              {/* Col 3: Cleared */}
              <div className="p-3 space-y-2.5 overflow-y-auto">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-tertiary font-bold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-tertiary"></span>
                    CLEARED &amp; RESTORED
                  </span>
                  <span className="px-1.5 py-0.2 bg-tertiary/20 text-tertiary rounded text-[10px] font-bold">{cleared.length} PASSABLE</span>
                </div>

                {cleared.map((c) => (
                  <div key={c.id} className="bg-surface-container border border-tertiary/40 rounded p-2.5 space-y-1 text-xs font-mono">
                    <div className="flex justify-between font-bold text-on-surface">
                      <span>{c.road}</span>
                      <span className="text-tertiary text-[10px]">100% Passable</span>
                    </div>
                    <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant text-[11px] space-y-0.5">
                      <div className="font-bold text-on-surface">{c.machinery}</div>
                      <div className="text-outline">Lead: {c.assignee}</div>
                    </div>
                    <div className="text-[10px] text-tertiary">Carriageway cleared &amp; verified by field engineer</div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* RIGHT: Ground Truth ML Feedback (40%) */}
          <section className="w-full xl:w-[40%] flex flex-col bg-surface-container-low overflow-y-auto p-4 space-y-4 font-mono text-xs">
            <div className="border-b border-outline-variant pb-2">
              <span className="text-primary font-bold uppercase tracking-wider block">GROUND-TRUTH VERIFICATION // ML FEEDBACK</span>
              <span className="text-sm font-bold text-on-surface">INCIDENT #S1-GJ-SH25: SH-25 (KM 42+100 - 44+800)</span>
            </div>

            <div className="bg-surface border border-outline-variant rounded p-3 space-y-2">
              <span className="text-secondary font-bold text-[11px]">QUANTITATIVE FIELD METRICS VS SAR PREDICTION</span>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="bg-surface-container p-2 rounded border border-outline-variant">
                  <span className="text-outline block">OBSERVED FIELD DEPTH</span>
                  <span className="text-lg font-bold text-on-surface">+0.38m</span>
                  <div className="text-[10px] text-tertiary">Δ -0.04m vs S1 Estimate</div>
                </div>
                <div className="bg-surface-container p-2 rounded border border-outline-variant">
                  <span className="text-outline block">SATELLITE SAR ESTIMATE</span>
                  <span className="text-lg font-bold text-primary">+0.42m</span>
                  <div className="text-[10px] text-outline">estimated (30 m DEM)</div>
                </div>
              </div>
            </div>

            <div className="bg-surface border border-outline-variant rounded p-3 space-y-2">
              <span className="text-primary font-bold text-[11px]">SAR ACCURACY FEEDBACK (SENTINEL-1 GROUND TRUTHING)</span>
              <label className="flex items-center gap-2 p-2 rounded bg-tertiary/10 border border-tertiary/40 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-tertiary font-bold text-[11px]">True Positive (Accurate Submergence Detection)</span>
              </label>
              <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant text-[10px] text-on-surface-variant">
                Observed water line matches Otsu <strong className="text-secondary">-17.41 dB</strong> backscatter null. Suggested offset: <strong className="text-tertiary">+0.2 dB</strong> for next pass.
              </div>
            </div>

            <button
              onClick={handleFeedback}
              disabled={isSubmitting}
              className="w-full py-2 bg-primary text-surface-container-lowest font-bold text-xs rounded hover:bg-surface-tint shadow active:scale-95 transition-all cursor-pointer disabled:opacity-50"
            >
              {isSubmitting ? 'SYNCHRONIZING WITH POSTGRESQL...' : (reportSubmitted ? 'FIELD REPORT SYNCHRONIZED ✓' : 'SUBMIT FIELD REPORT & SYNC SAR MODEL')}
            </button>
          </section>
        </main>
      </div>
    </div>
  );
}
