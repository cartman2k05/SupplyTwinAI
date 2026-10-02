import React, { useState, useEffect, useRef } from 'react';
import KPICard from '../components/dashboard/KPICard';
import RiskChart from '../components/dashboard/RiskChart';
import DelayChart from '../components/dashboard/DelayChart';
import DisruptionsTable from '../components/dashboard/DisruptionsTable';
import SimulationControl from '../components/dashboard/SimulationControl';
import { SimulationWebSocket } from '../services/websocket';
import { dataApi } from '../services/api';
import { Truck, AlertCircle, ShieldCheck, Lightbulb, Filter, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [selectedMarket, setSelectedMarket] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [telemetry, setTelemetry] = useState(null);
  const [wsStatus, setWsStatus] = useState('connecting');
  const [disruptions, setDisruptions] = useState([]);
  const wsRef = useRef(null);

  const [kpiData, setKpiData] = useState({
    activeShipments: 65752,
    atRiskShipments: 14,
    avgReliability: '94.2%',
    pendingRecommendations: 3,
  });

  useEffect(() => {
    // Connect WebSocket live telemetry stream
    const simWs = new SimulationWebSocket({
      onTelemetry: (data) => {
        setTelemetry(data);
        if (data.live_shipments_count !== undefined) {
          setKpiData(prev => ({
            ...prev,
            activeShipments: data.live_shipments_count,
            atRiskShipments: data.delayed_shipments || 0,
          }));
        }
        if (data.recent_disruptions && data.recent_disruptions.length > 0) {
          const formatted = data.recent_disruptions.map(d => ({
            id: `EVT-${d.event_id}`,
            global_id: d.target_global_id,
            target: d.target_global_id,
            type: d.event_type,
            severity: Math.round(d.severity * 100),
            status: d.severity > 0.8 ? 'HIGH RISK' : 'MEDIUM RISK',
            time: 'Just now',
          }));
          setDisruptions(formatted);
        }
      },
      onDisruption: (evt) => {
        const formattedEvt = {
          id: `EVT-${evt.event_id}`,
          global_id: evt.target_global_id,
          target: evt.target_global_id,
          type: evt.event_type,
          severity: Math.round(evt.severity * 100),
          status: evt.severity > 0.8 ? 'HIGH RISK' : 'MEDIUM RISK',
          time: 'Just now',
        };
        setDisruptions(prev => [formattedEvt, ...prev.slice(0, 9)]);
      },
      onStatusChange: (status) => {
        setWsStatus(status);
      },
    });

    wsRef.current = simWs;
    simWs.connect();

    // Fetch baseline data from REST API
    Promise.all([
      dataApi.getShipments(100).catch(() => []),
      dataApi.getSuppliers(50).catch(() => []),
    ]).then(([shipments, suppliers]) => {
      if (suppliers.length > 0) {
        const avgOntime = suppliers.reduce((acc, s) => acc + s.on_time_rate, 0) / suppliers.length;
        setKpiData(prev => ({
          ...prev,
          avgReliability: `${(avgOntime * 100).toFixed(1)}%`,
        }));
      }
      setLoading(false);
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    if (wsRef.current && wsRef.current.socket && wsRef.current.socket.readyState === WebSocket.OPEN) {
      wsRef.current.socket.send('ping');
    }
    setTimeout(() => setLoading(false), 500);
  };

  return (
    <div className="space-y-6">
      {/* Header & Market Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Supply Chain Manager Dashboard</h1>
          <p className="text-xs text-slate-400">
            Real-time Digital Twin telemetry, multi-agent risk signals, and autonomous recommendations.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Market:</span>
            <select
              value={selectedMarket}
              onChange={(e) => setSelectedMarket(e.target.value)}
              className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-slate-900">All Markets (Global)</option>
              <option value="USCA" className="bg-slate-900">USCA (North America)</option>
              <option value="Europe" className="bg-slate-900">Europe</option>
              <option value="LATAM" className="bg-slate-900">LATAM (Latin America)</option>
              <option value="Pacific Asia" className="bg-slate-900">Pacific Asia</option>
            </select>
          </div>

          <button
            onClick={handleRefresh}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg transition-colors"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Simulation Engine Telemetry Controls Bar */}
      <SimulationControl
        telemetry={telemetry}
        wsStatus={wsStatus}
        onTriggerUpdate={handleRefresh}
      />

      {/* Primary KPI Grid (Visible above the fold at 1366x768, §4.7 REQ-2) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active In-Transit Shipments"
          value={loading ? '...' : kpiData.activeShipments.toLocaleString()}
          subtext="Simulated Live Fleet"
          icon={Truck}
          color="indigo"
          trend={{ label: '+2.4%', positive: true }}
        />
        <KPICard
          title="At-Risk / Delayed Shipments"
          value={loading ? '...' : kpiData.atRiskShipments}
          subtext="Disruption Impacted"
          icon={AlertCircle}
          color="rose"
          trend={{ label: kpiData.atRiskShipments > 0 ? 'Action Required' : 'Optimal', positive: kpiData.atRiskShipments === 0 }}
        />
        <KPICard
          title="Supplier Reliability"
          value={loading ? '...' : kpiData.avgReliability}
          subtext="Primary + Alternate Pool"
          icon={ShieldCheck}
          color="emerald"
          trend={{ label: 'Stable', positive: true }}
        />
        <KPICard
          title="Pending Recommendations"
          value={loading ? '...' : kpiData.pendingRecommendations}
          subtext="Requires Manager Action"
          icon={Lightbulb}
          color="amber"
          trend={{ label: 'Human-in-Loop', positive: false }}
        />
      </div>

      {/* Interactive Charts Section (§4.7 REQ-3) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="h-64">
          <RiskChart
            lowCount={Math.max(10, kpiData.activeShipments - kpiData.atRiskShipments)}
            medCount={Math.max(2, kpiData.atRiskShipments)}
            highCount={telemetry?.active_disruptions_count || 0}
          />
        </div>
        <div className="h-64">
          <DelayChart />
        </div>
      </div>

      {/* Active Disruption Signals Table */}
      <DisruptionsTable events={disruptions} />
    </div>
  );
}
