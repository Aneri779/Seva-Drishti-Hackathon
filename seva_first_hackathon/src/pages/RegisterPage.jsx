// PAGE 2: Official Onboarding & Unit Registration (Live PostgreSQL Integration)
import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../api/client';
import { showToast } from '../components/common/Toast';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    designation: '',
    role: 'rb_ee',
    district_id: '1',
    govt_email: '',
    mobile_number: '',
  });
  const [file, setFile] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);
  const [districts, setDistricts] = useState([]);
  const [roles, setRoles] = useState([]);
  const [sysStatus, setSysStatus] = useState(null);

  useEffect(() => {
    // Load metadata and system status from PostgreSQL
    api.get('/meta/districts')
      .then(setDistricts)
      .catch((e) => console.error('Districts load error:', e));

    api.get('/meta/roles')
      .then(setRoles)
      .catch((e) => console.error('Roles load error:', e));

    api.get('/system/status')
      .then(setSysStatus)
      .catch((e) => console.error('Status load error:', e));

    const el = document.getElementById('telemetry-time');
    if (!el) return;
    const tick = () => {
      const t = new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Kolkata', hour12: false });
      el.textContent = t + ' IST';
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setStatusMsg('');

    // Strict 10-digit mobile number validation
    const cleanMob = formData.mobile_number.replace(/\D/g, '');
    if (cleanMob.length !== 10) {
      showToast('Mobile number must be exactly 10 digits (e.g. 9876543210)', 'error');
      setErr('Mobile number must be exactly 10 digits.');
      return;
    }

    if (!formData.govt_email || !formData.full_name) {
      showToast('Please fill all required registration fields', 'error');
      return;
    }

    setLoading(true);

    try {
      // Use multipart FormData for file and field data
      const data = new FormData();
      data.append('full_name', formData.full_name);
      data.append('designation', formData.designation);
      data.append('role', formData.role);
      data.append('district_id', formData.district_id);
      data.append('govt_email', formData.govt_email);
      data.append('mobile_number', cleanMob);
      if (file) {
        data.append('id_document', file);
      }

      const res = await api('/auth/register', {
        method: 'POST',
        form: data,
      });

      setStatusMsg(res.message || 'Registration submitted. Awaiting administrative approval.');
      showToast('Unit registered successfully! Forwarding to Login...', 'success');

      // Auto redirect to login with prefilled mobile parameter after 1.5s
      setTimeout(() => {
        navigate(`/login?mobile=${cleanMob}`);
      }, 1500);
    } catch (error) {
      const msg = error.message || 'Registration failed';
      setErr(msg);
      showToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tactical-grid-bg flex-1 flex flex-col p-4 md:p-8">
      <div className="max-w-4xl mx-auto w-full bg-surface-container-low border border-outline-variant rounded-xl shadow-2xl p-6 md:p-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-outline-variant/40 gap-4">
          <div>
            <div className="flex items-center gap-2 text-primary font-mono text-xs font-bold uppercase tracking-wider">
              <span className="material-symbols-outlined text-sm">badge</span>
              Gujarat Roads &amp; Buildings Official Onboarding
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-on-surface mt-1">Operational Unit Registration</h1>
          </div>
          <div className="text-right">
            <div id="telemetry-time" className="font-mono text-xs text-primary font-bold">--:--:-- IST</div>
            <div className="text-[10px] font-mono text-green-400 mt-0.5">
              ● {sysStatus?.database || 'PostgreSQL Connected'}
            </div>
          </div>
        </div>

        {/* Feedback Alerts */}
        {statusMsg && (
          <div className="my-4 p-4 rounded bg-green-950/40 border border-green-500 text-green-300 text-xs font-mono flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">check_circle</span>
            <span>{statusMsg}</span>
          </div>
        )}
        {err && (
          <div className="my-4 p-4 rounded bg-red-950/40 border border-error text-red-300 text-xs font-mono flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">error</span>
            <span>{err}</span>
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Full Officer Name *</label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="e.g. V. K. Patel"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Official Designation *</label>
              <input
                type="text"
                name="designation"
                value={formData.designation}
                onChange={handleChange}
                required
                placeholder="e.g. Executive Engineer (R&B)"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Operational Role *</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              >
                {roles.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Assigned District *</label>
              <select
                name="district_id"
                value={formData.district_id}
                onChange={handleChange}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              >
                {districts.map((d) => (
                  <option key={d.id} value={d.id}>{d.name} ({d.name_gu})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Official Gov / Departmental Email *</label>
              <input
                type="email"
                name="govt_email"
                value={formData.govt_email}
                onChange={handleChange}
                required
                placeholder="officer@gujarat.gov.in"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
              <span className="text-[10px] text-on-surface-variant">Allowed: @gujarat.gov.in, @gov.in, @nic.in, @gsrtc.in</span>
            </div>

            <div>
              <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Official Mobile (+91) *</label>
              <input
                type="text"
                name="mobile_number"
                value={formData.mobile_number}
                onChange={handleChange}
                required
                placeholder="9876543210"
                className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
              <span className="text-[10px] text-on-surface-variant">Used for 2-factor OTP verification</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono text-on-surface-variant uppercase mb-1">Departmental ID Document / Order Copy (Optional)</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full bg-surface-container-lowest border border-outline-variant rounded px-3 py-2 text-xs font-mono text-on-surface-variant file:mr-4 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:font-mono file:bg-surface-container-high file:text-primary"
            />
          </div>

          <div className="pt-4 flex items-center justify-between">
            <Link to="/login" className="text-xs font-mono text-primary hover:underline flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">arrow_back</span>
              Already registered? Login here
            </Link>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-primary text-surface-container-lowest font-mono text-xs font-bold rounded hover:bg-surface-tint disabled:opacity-50 transition shadow"
            >
              {loading ? 'Submitting Unit Registration...' : 'Submit Unit Registration'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
