import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import ToastContainer from './components/common/Toast';

// Public & Authentication Pages
import HomePage from './pages/HomePage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';

// Operational Command Center & Telemetry Workstations
import DashboardPage from './pages/DashboardPage';
import BackscatterInspector from './pages/BackscatterInspector';
import ChainageRegistry from './pages/ChainageRegistry';
import ConvoyRouting from './pages/ConvoyRouting';
import NotificationOps from './pages/NotificationOps';
import BulletinGenerator from './pages/BulletinGenerator';
import FieldDispatch from './pages/FieldDispatch';
import AdminConfig from './pages/AdminConfig';

export default function App() {
  return (
    <AuthProvider>
      <ToastContainer />
      <BrowserRouter>
        <Routes>
          {/* Public & Access Gateways (Wrapped in Master Layout) */}
          <Route path="/" element={<Layout><HomePage /></Layout>} />
          <Route path="/register" element={<Layout><RegisterPage /></Layout>} />
          <Route path="/login" element={<Layout><LoginPage /></Layout>} />

          {/* Tactical Operational Workstations Protected with Role Guards */}
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/backscatter" element={<ProtectedRoute><BackscatterInspector /></ProtectedRoute>} />
          <Route path="/chainage-registry" element={<ProtectedRoute><ChainageRegistry /></ProtectedRoute>} />
          <Route path="/convoy-routing" element={<ProtectedRoute roles={['seoc_officer', 'rb_ee', 'ndrf', 'gsrtc', 'admin']}><ConvoyRouting /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute roles={['seoc_officer', 'admin']}><NotificationOps /></ProtectedRoute>} />
          <Route path="/bulletin" element={<ProtectedRoute roles={['seoc_officer', 'rb_ee', 'admin']}><BulletinGenerator /></ProtectedRoute>} />
          <Route path="/dispatch" element={<ProtectedRoute roles={['rb_ee', 'admin']}><FieldDispatch /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute roles={['admin']}><AdminConfig /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
