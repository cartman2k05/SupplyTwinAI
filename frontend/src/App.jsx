import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Shipments from './pages/Shipments';
import Inventory from './pages/Inventory';
import Suppliers from './pages/Suppliers';
import DigitalTwinGraph from './pages/DigitalTwinGraph';
import AIAssistant from './pages/AIAssistant';
import RecommendationCenter from './pages/RecommendationCenter';
import AdminConfig from './pages/AdminConfig';
import EtlMonitor from './pages/EtlMonitor';

function AuthGuard() {
  const { token, loading } = useAuth();
  if (loading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">Loading session...</div>;
  }
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

function RoleGuard({ requiredRole }) {
  const { role } = useAuth();
  if (role !== requiredRole && role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}

function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Login Route */}
          <Route path="/login" element={<Login />} />

          {/* Protected Application Routes */}
          <Route element={<AuthGuard />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/shipments" element={<Shipments />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/suppliers" element={<Suppliers />} />

              {/* Admin Only Routes */}
              <Route element={<RoleGuard requiredRole="admin" />}>
                <Route path="/admin/config" element={<AdminConfig />} />
                <Route path="/admin/etl" element={<EtlMonitor />} />
              </Route>

              {/* Phase 5 Graph Route, Phase 6 Chat Route, Phase 8 Recommendation Center */}
              <Route path="/graph" element={<DigitalTwinGraph />} />
              <Route path="/chat" element={<AIAssistant />} />
              <Route path="/recommendations" element={<RecommendationCenter />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
