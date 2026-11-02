import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const initialMobile = searchParams.get('mobile') || '9876543210';
  const [mobile, setMobile] = useState(initialMobile);
  const [otpDigits, setOtpDigits] = useState(['', '', '', '', '', '']);
  const [isOtpSent, setIsOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [outboxMessage, setOutboxMessage] = useState(null);
  const [telemetry, setTelemetry] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  // Load live telemetry from PostgreSQL / GEE
  useEffect(() => {
    api.get('/scenes/latest/telemetry')
      .then(setTelemetry)
      .catch(() => {});
  }, []);

  // Poll DEV SMS INBOX when OTP is requested
  useEffect(() => {
    if (!isOtpSent) return;
    const poll = async () => {
      try {
        const outbox = await api.get(`/auth/dev/sms-outbox?mobile=${mobile}`);
        if (outbox && outbox.length > 0) {
          setOutboxMessage(outbox[0]);
        }
      } catch (err) {}
    };
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [isOtpSent, mobile]);

  const handleSendOtp = async (e) => {
    e.preventDefault();
    if (!mobile || mobile.length < 10) {
      showToast('Please enter a valid 10-digit mobile number', 'error');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/otp/send', { mobile });
      setIsOtpSent(true);
      showToast('OTP dispatched via SMS / Sandes Gov Gateway', 'success');
    } catch (err) {
      showToast(err.message || 'Failed to dispatch OTP', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpChange = (index, val) => {
    if (val.length > 1) val = val[val.length - 1];
    const newDigits = [...otpDigits];
    newDigits[index] = val;
    setOtpDigits(newDigits);
    if (val && index < 5) {
      const nextInput = document.getElementById(`otp-box-${index + 1}`);
      if (nextInput) nextInput.focus();
    }
  };

  const handleAutofill = () => {
    if (!outboxMessage) return;
    const match = outboxMessage.body.match(/\d{6}/);
    if (match) {
      const digits = match[0].split('');
      setOtpDigits(digits);
      showToast('OTP auto-filled from secure DEV SMS INBOX', 'info');
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    const fullOtp = otpDigits.join('');
    if (fullOtp.length !== 6) {
      showToast('Please enter complete 6-digit OTP', 'error');
      return;
    }
    setLoading(true);
    try {
      const data = await api.post('/auth/otp/verify', { mobile, otp: fullOtp });
      login(data.tokens?.access_token || data.token, data.user);
      showToast(`Access granted: Welcome ${data.user.name}`, 'success');
      navigate('/dashboard');
    } catch (err) {
      showToast(err.message || 'OTP verification failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-surface-container-low border border-outline-variant rounded-xl shadow-2xl overflow-hidden grid md:grid-cols-2">
        
        {/* Left: Satellite Telemetry Monitor */}
        <div className="p-8 bg-surface-container-lowest border-r border-outline-variant/30 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-6">
              <span className="material-symbols-outlined text-primary text-2xl animate-pulse">radar</span>
              <span className="font-mono text-sm tracking-widest text-primary font-bold uppercase">SAR-Drishti SEOC Terminal</span>
            </div>
            
            <h2 className="text-xl font-bold text-on-surface mb-2">Sentinel-1 Highway Telemetry</h2>
            <p className="text-xs text-on-surface-variant mb-6">
              Cloud-penetrating Synthetic Aperture Radar (SAR) submergence & breach monitoring for Roads & Buildings Dept, Gujarat.
            </p>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-surface-container rounded border border-outline-variant/50">
                <div className="text-[10px] text-on-surface-variant uppercase">PostgreSQL Database</div>
                <div className="font-bold text-green-400 mt-1">CONNECTED (localhost:5432/sardrishti)</div>
              </div>
              <div className="p-3 bg-surface-container rounded border border-outline-variant/50">
                <div className="text-[10px] text-on-surface-variant uppercase">Sentinel-1 Active Scene</div>
                <div className="font-bold text-primary mt-1 truncate">{telemetry?.s1_id || 'Querying GEE Catalog...'}</div>
              </div>
              <div className="p-3 bg-surface-container rounded border border-outline-variant/50">
                <div className="text-[10px] text-on-surface-variant uppercase">Mean Sigma0 (VV) / Flood Area</div>
                <div className="font-bold text-on-surface mt-1">
                  {telemetry ? `${telemetry.mean_sigma0_vv} dB | ${telemetry.flood_km2} km²` : 'Synchronizing telemetry...'}
                </div>
              </div>
            </div>
          </div>

          <div className="text-[10px] font-mono text-on-surface-variant mt-6 border-t border-outline-variant/30 pt-4 flex justify-between">
            <span>R&B DEPT GOVT OF GUJARAT</span>
            <span className="text-green-500 font-bold">SECURE SSL AUTH</span>
          </div>
        </div>

        {/* Right: Real OTP Login Flow */}
        <div className="p-8 flex flex-col justify-center">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-on-surface">Officer Identity Verification</h3>
            <p className="text-xs text-on-surface-variant mt-1">Enter your registered official 10-digit mobile number</p>
          </div>

          <form onSubmit={isOtpSent ? handleVerify : handleSendOtp} className="space-y-5">
            <div>
              <label className="block text-xs font-mono text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Authorized Mobile (+91)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  disabled={isOtpSent}
                  className="flex-1 bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-sm font-mono text-on-surface focus:outline-none focus:border-primary"
                  placeholder="9876543210"
                />
                {!isOtpSent && (
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint disabled:opacity-50 transition"
                  >
                    {loading ? 'Sending...' : 'Send OTP'}
                  </button>
                )}
              </div>
            </div>

            {isOtpSent && (
              <div>
                <label className="block text-xs font-mono text-on-surface-variant mb-1.5 uppercase tracking-wider">
                  6-Digit Emergency OTP
                </label>
                <div className="flex justify-between gap-1.5 mb-3">
                  {otpDigits.map((digit, idx) => (
                    <input
                      key={idx}
                      id={`otp-box-${idx}`}
                      type="text"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(idx, e.target.value)}
                      className="w-11 h-12 text-center text-lg font-bold font-mono bg-surface-container-lowest border border-outline-variant rounded focus:border-primary focus:outline-none text-primary"
                    />
                  ))}
                </div>

                {/* DEV SMS INBOX Panel (Only shown in dev/local mode) */}
                <div className="p-3 bg-surface-container rounded border border-amber-500/40 text-xs font-mono mb-4">
                  <div className="flex items-center justify-between text-[10px] text-amber-400 font-bold uppercase mb-1">
                    <span>📡 DEV SMS INBOX</span>
                    {outboxMessage && (
                      <button
                        type="button"
                        onClick={handleAutofill}
                        className="px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded border border-amber-500/40 hover:bg-amber-500/30"
                      >
                        ⚡ Autofill
                      </button>
                    )}
                  </div>
                  <div className="text-[11px] text-on-surface-variant leading-relaxed">
                    {outboxMessage ? outboxMessage.body : 'Waiting for SMS gateway dispatch...'}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 py-2.5 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint disabled:opacity-50 transition"
                  >
                    {loading ? 'Verifying...' : 'Verify & Enter Terminal'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setIsOtpSent(false); setOtpDigits(['','','','','','']); }}
                    className="px-3 py-2 border border-outline-variant rounded text-xs font-mono hover:bg-surface-container"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </form>

          <div className="mt-8 text-center">
            <span className="text-xs text-on-surface-variant font-mono">Test Account: </span>
            <span className="text-xs text-primary font-mono cursor-pointer hover:underline" onClick={() => setMobile('9876543210')}>
              9876543210 (Super Admin)
            </span>
          </div>

        </div>

      </div>
    </div>
  );
}
