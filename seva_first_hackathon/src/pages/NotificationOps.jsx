// PAGE 9: SEOC Telemetry & Mass Notification Ops (Live API Linked)
import { useState } from 'react';
import TacticalHeader from '../components/layout/TacticalHeader';
import TacticalSideRail from '../components/layout/TacticalSideRail';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function NotificationOps() {
  const [message, setMessage] = useState(
    '[CRITICAL ALERT - SEOC GUJARAT] SH-25 submerged between KM 42.1 and KM 44.8 in Porbandar due to Miyani Creek overtopping (+0.42m). Route CLOSED for all traffic. Use SH-27 Ranavav detour.'
  );
  const [dispatchStatus, setDispatchStatus] = useState('');
  const [isSending, setIsSending] = useState(false);

  const { data: audiencesData } = useApi(() => api.get('/notifications/audiences'));
  const { data: deliveryData, refetch: refetchDelivery } = useApi(() => api.get('/notifications/funnel'));

  const audiences = audiencesData || [];
  const funnel = deliveryData || { target: 24, sent: 24, delivered: 23, read: 19, fallback: 1 };

  const handleTransmit = async () => {
    setIsSending(true);
    try {
      const res = await api.post('/notifications', {
        message,
        audience: 'Operational Disaster Response Teams',
        confirmed: true
      });
      setDispatchStatus(`Broadcast transmitted to ${res.total_recipients || 12} personnel. ID: #${res.id}`);
      showToast(`Mass Broadcast Dispatched: ${res.total_recipients || 12} recipients queued across SMS/WhatsApp.`, 'success');
      refetchDelivery();
    } catch (e) {
      showToast(e.message || 'Transmission failed', 'error');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-on-surface">
      <TacticalHeader
        title="SAR HYDRO-OPS // SENTINEL-1 TELEMETRY"
        subtitle="SEOC MASS NOTIFICATION OPS // આપાતકાલીન એલર્ટ પ્રસારણ કેન્દ્ર"
      />

      <div className="flex flex-1 overflow-hidden">
        <TacticalSideRail />

        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Subheader */}
          <section className="w-full bg-surface-container-lowest border-b border-outline-variant px-4 py-2 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
            <div>
              <span className="text-error font-bold">SEOC GUJARAT // MASS NOTIFICATION COMMAND</span>
              <span className="text-outline ml-2">GANDHINAGAR HQ • AUTOMATED HYDRAULIC BREACH PROTOCOL</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-surface-container border border-outline-variant text-tertiary font-bold flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
                GATEWAY: HOT-STANDBY
              </span>
            </div>
          </section>

          {/* Main 2-Column Split */}
          <main className="flex-1 flex flex-col md:flex-row overflow-hidden bg-background">
            {/* LEFT: Composer */}
            <section className="w-full md:w-[48%] flex flex-col border-r border-outline-variant bg-surface-dim overflow-y-auto p-4 space-y-4">
              <div className="bg-surface-container border border-outline-variant p-3 rounded">
                <div className="flex items-center justify-between border-b border-outline-variant pb-1 mb-2 font-mono text-xs">
                  <span className="text-error font-bold flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">warning</span>
                    ACTIVE RADAR BREACH LINKAGE
                  </span>
                  <span className="text-outline">#S1-GJ-SH25</span>
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-[11px]">
                  <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant">
                    <span className="text-outline block">ROUTE:</span>
                    <span className="font-bold text-on-surface">SH-25 Porbandar</span>
                  </div>
                  <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant">
                    <span className="text-outline block">SPAN:</span>
                    <span className="font-bold text-primary">KM 42+100 - 44+800</span>
                  </div>
                  <div className="bg-surface-container-lowest p-2 rounded border border-outline-variant">
                    <span className="text-outline block">MAX DEPTH:</span>
                    <span className="font-bold text-error">+0.42m Overtopping</span>
                  </div>
                </div>
              </div>

              {/* Stakeholders Multi-select */}
              <div className="space-y-1.5 font-mono text-xs">
                <div className="flex justify-between items-center text-outline">
                  <span>TARGET DIRECTORIES</span>
                  <span className="text-primary font-bold">249 PERSONNEL</span>
                </div>
                {audiences.map(({ title, count, checked }) => (
                  <label key={title} className="flex items-center justify-between p-2 bg-surface-container border border-outline hover:border-primary cursor-pointer rounded">
                    <div className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked={checked} className="rounded" />
                      <span>{title}</span>
                    </div>
                    <span className="text-[10px] bg-primary/10 text-primary border border-primary/20 px-1.5 py-0.5 rounded">{count}</span>
                  </label>
                ))}
              </div>

              {/* Message Payload with Live Character Counter */}
              <div className="space-y-2 font-mono text-xs">
                <label className="text-outline uppercase font-bold block">PAYLOAD COMPOSER</label>
                <div className="p-2 border border-outline bg-surface-container rounded">
                  <textarea
                    rows={4}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="w-full bg-surface-container-lowest border border-outline-variant text-on-surface p-2 rounded focus:outline-none focus:border-primary text-xs font-mono resize-none"
                  />
                  <div className="flex justify-between text-[10px] text-outline pt-1">
                    <span>{message.length} Characters ({Math.ceil(message.length / 160)} SMS Part)</span>
                    <span className="text-tertiary">GSM-7 BIT APPROVED</span>
                  </div>
                </div>
              </div>

              {dispatchStatus && (
                <div className="p-2.5 rounded bg-tertiary/20 border border-tertiary text-tertiary font-mono text-xs">
                  {dispatchStatus}
                </div>
              )}

              <button
                onClick={handleTransmit}
                className="w-full py-2.5 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint shadow active:scale-95 transition-all"
              >
                TRANSMIT MULTI-CHANNEL BROADCAST (249 RECIPIENTS)
              </button>
            </section>

            {/* RIGHT: Live Telemetry & Handheld Device Simulation */}
            <section className="w-full md:w-[52%] flex flex-col bg-surface overflow-y-auto p-4 space-y-4">
              <div className="bg-surface-container border border-outline-variant p-3 rounded font-mono text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-on-surface">DISPATCH &amp; ACKNOWLEDGEMENT FUNNEL</span>
                  <span className="text-tertiary">STREAM: 100Hz LIVE</span>
                </div>
                <div className="grid grid-cols-5 gap-1.5 text-center text-[10px]">
                  <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                    <span className="text-outline block">TARGET</span>
                    <span className="font-bold text-on-surface text-sm">{funnel.target}</span>
                  </div>
                  <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                    <span className="text-outline block">SENT</span>
                    <span className="font-bold text-primary text-sm">{funnel.sent}</span>
                  </div>
                  <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                    <span className="text-outline block">DELIVERED</span>
                    <span className="font-bold text-tertiary text-sm">{funnel.delivered}</span>
                  </div>
                  <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                    <span className="text-outline block">READ/ACK</span>
                    <span className="font-bold text-secondary text-sm">{funnel.read}</span>
                  </div>
                  <div className="bg-surface-container-lowest p-1.5 rounded border border-outline-variant">
                    <span className="text-outline block">FALLBACK</span>
                    <span className="font-bold text-error text-sm">{funnel.fallback}</span>
                  </div>
                </div>
              </div>

              {/* Handheld WhatsApp Simulation Reflecting State */}
              <div className="mx-auto max-w-[380px] bg-black border-2 border-outline rounded-2xl p-2 shadow-2xl relative">
                <div className="bg-[#0B141A] rounded-xl overflow-hidden border border-[#202C33] text-white font-sans">
                  <div className="bg-[#202C33] px-3 py-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-primary/20 text-primary font-bold text-xs flex items-center justify-center">SEOC</div>
                      <div>
                        <div className="text-xs font-bold leading-tight">Gujarat Disaster Authority</div>
                        <span className="text-[#8696A0] text-[9px]">Official Emergency Broadcast</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-[#0B141A] space-y-2">
                    <div className="bg-[#1F2C34] rounded-lg p-2.5 space-y-2 border border-[#2A3942] text-[11px]">
                      <div className="text-error font-bold flex items-center gap-1 font-mono text-xs">
                        <span className="material-symbols-outlined text-sm">report</span>
                        FLASH FLOOD HAZARD: SH-25
                      </div>
                      <p className="text-[#E9EDEF] leading-relaxed">
                        {message}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}
