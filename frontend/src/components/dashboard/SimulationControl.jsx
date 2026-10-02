import React, { useState } from 'react';
import { Play, Pause, FastForward, RotateCcw, Zap, Wifi, RefreshCw, AlertCircle } from 'lucide-react';
import { apiFetch } from '../../services/api';

const SCENARIO_OPTIONS = [
  { id: 'SCENARIO-SUP-01', name: 'Primary Supplier Factory Shutdown (Supplier:1)' },
  { id: 'SCENARIO-LOG-01', name: 'West Coast Port Congestion (Shipment:77202)' },
  { id: 'SCENARIO-WTH-01', name: 'Midwest Blizzard Transit Corridor (Warehouse:1)' },
  { id: 'SCENARIO-STK-01', name: 'Fulfillment Stockout Surge (Inventory:101)' },
  { id: 'SCENARIO-GEO-01', name: 'Border Customs Policy Inspection Shift (Supplier:5)' },
  { id: 'SCENARIO-CMP-01', name: 'Typhoon & Secondary Supplier Outage (Supplier:2)' },
];

export default function SimulationControl({ telemetry, wsStatus, onTriggerUpdate }) {
  const [selectedScenario, setSelectedScenario] = useState('SCENARIO-SUP-01');
  const [loading, setLoading] = useState(false);

  const isRunning = telemetry?.is_running || false;
  const simTime = telemetry?.sim_time ? new Date(telemetry.sim_time).toLocaleString() : 'Not Started';
  const speed = telemetry?.speed_multiplier || 1.0;

  const handleControl = async (action, extraParams = {}) => {
    setLoading(true);
    try {
      await apiFetch('/simulation/control', {
        method: 'POST',
        body: JSON.stringify({ action, ...extraParams }),
      });
      if (onTriggerUpdate) onTriggerUpdate();
    } catch (err) {
      console.error(`Simulation ${action} error:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleInject = async () => {
    setLoading(true);
    try {
      await apiFetch('/simulation/inject', {
        method: 'POST',
        body: JSON.stringify({ scenario_id: selectedScenario }),
      });
      if (onTriggerUpdate) onTriggerUpdate();
    } catch (err) {
      console.error('Disruption injection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = () => {
    switch (wsStatus) {
      case 'connected':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Live WS Stream</span>
          </span>
        );
      case 'polling':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-400 border border-amber-800/60">
            <RefreshCw className="w-3 h-3 animate-spin text-amber-400" />
            <span>HTTP Polling (5s)</span>
          </span>
        );
      case 'reconnecting':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800/60">
            <Wifi className="w-3 h-3 animate-pulse text-blue-400" />
            <span>Reconnecting...</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <AlertCircle className="w-3 h-3" />
            <span>Disconnected</span>
          </span>
        );
    }
  };

  return (
    <div className="glass-card rounded-xl p-5 mb-6 border border-slate-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Clock Status & Title */}
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <h2 className="text-base font-bold text-white tracking-wide">Simulation Engine Telemetry</h2>
            {getStatusBadge()}
          </div>
          <div className="flex items-center space-x-4 text-xs text-slate-400">
            <span>Sim Clock: <strong className="text-indigo-300 font-mono">{simTime}</strong></span>
            <span>Ticks: <strong className="text-slate-200 font-mono">{telemetry?.total_ticks || 0}</strong></span>
            <span>Speed: <strong className="text-emerald-400 font-mono">{speed}x</strong></span>
          </div>
        </div>

        {/* Center: Engine Controls */}
        <div className="flex items-center space-x-2">
          {isRunning ? (
            <button
              onClick={() => handleControl('pause')}
              disabled={loading}
              className="px-3.5 py-2 bg-amber-600/90 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-lg shadow-amber-900/30"
            >
              <Pause className="w-3.5 h-3.5" />
              <span>Pause Clock</span>
            </button>
          ) : (
            <button
              onClick={() => handleControl('start')}
              disabled={loading}
              className="px-3.5 py-2 bg-emerald-600/90 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-lg shadow-emerald-900/30"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Start Clock</span>
            </button>
          )}

          <button
            onClick={() => handleControl('step')}
            disabled={loading}
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-all border border-slate-700"
            title="Step clock forward 1 sim hour"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>+1h Step</span>
          </button>

          <select
            value={speed}
            onChange={(e) => handleControl('start', { speed: parseFloat(e.target.value) })}
            className="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-2 text-xs font-medium focus:outline-none focus:border-indigo-500"
          >
            <option value={1.0}>1x Speed</option>
            <option value={2.0}>2x Speed</option>
            <option value={5.0}>5x Speed</option>
            <option value={10.0}>10x Speed</option>
          </select>

          <button
            onClick={() => handleControl('reset', { seed: 42 })}
            disabled={loading}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded-lg text-xs transition-all border border-slate-700"
            title="Reset Simulation Engine to Seed 42"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Right: Disruption Injection Controls */}
        <div className="flex items-center space-x-2 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-2 text-xs font-medium focus:outline-none focus:border-indigo-500 max-w-[220px] truncate"
          >
            {SCENARIO_OPTIONS.map((sc) => (
              <option key={sc.id} value={sc.id}>
                {sc.name}
              </option>
            ))}
          </select>

          <button
            onClick={handleInject}
            disabled={loading}
            className="px-3 py-2 bg-rose-600/90 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-lg shadow-rose-900/30 shrink-0"
          >
            <Zap className="w-3.5 h-3.5 text-amber-300" />
            <span>Inject Disruption</span>
          </button>
        </div>
      </div>
    </div>
  );
}
