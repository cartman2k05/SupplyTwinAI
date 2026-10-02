import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Database,
  Play,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  Clock,
  RefreshCw,
  Download,
  Activity,
  Layers
} from 'lucide-react';

export default function EtlMonitor() {
  const { token } = useAuth();
  const [etlRuns, setEtlRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningEtl, setRunningEtl] = useState(false);

  const fetchEtlHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/etl/history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEtlRuns(data.etl_runs || data || []);
      }
    } catch (err) {
      console.error('Failed to fetch ETL run history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEtlHistory();
  }, [token]);

  const handleTriggerEtl = async () => {
    setRunningEtl(true);
    try {
      const res = await fetch('/api/v1/etl/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        }
      });
      if (res.ok) {
        await fetchEtlHistory();
      } else {
        const err = await res.json();
        alert(`ETL Run failed: ${err.detail || 'Error executing ETL pipeline'}`);
      }
    } catch (err) {
      console.error('ETL execution error:', err);
    } finally {
      setRunningEtl(false);
    }
  };

  const handleDownloadCsv = (resource) => {
    window.open(`/api/v1/reports/export/${resource}`, '_blank');
  };

  // Compute KPI Aggregates
  const totalLoaded = etlRuns.reduce((acc, r) => acc + (r.loaded_records || 0), 0);
  const totalRejected = etlRuns.reduce((acc, r) => acc + (r.rejected_records || 0), 0);
  const totalFlagged = etlRuns.reduce((acc, r) => acc + (r.flagged_records || 0), 0);
  const avgDuration = etlRuns.length > 0
    ? (etlRuns.reduce((acc, r) => acc + (r.duration_seconds || 0), 0) / etlRuns.length).toFixed(2)
    : '0.00';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
            <Database className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              ETL Run Monitor & Audit Log
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                §4.1 REQ-4
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Data ingestion audit trail, loaded/rejected record counts, seeds, and export management.
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchEtlHistory}
            className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors border border-slate-700"
            title="Refresh History"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleTriggerEtl}
            disabled={runningEtl}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/20"
          >
            {runningEtl ? (
              <Activity className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{runningEtl ? 'Running Pipeline...' : 'Run Incremental ETL'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Records Loaded</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">
            {totalLoaded.toLocaleString()}
          </div>
          <div className="text-[11px] text-emerald-400 font-medium">Valid DataCo Ingestion</div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Rejected Records</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400 font-mono">
            {totalRejected.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400">Referential Integrity Drops</div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Flagged Synthetic Fields</span>
            <CheckCircle2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">
            {totalFlagged.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400">Enriched Synthetic Tables</div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Avg Pipeline Duration</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-indigo-400 font-mono">
            {avgDuration} s
          </div>
          <div className="text-[11px] text-slate-400">Postgres + Neo4j Sync</div>
        </div>
      </div>

      {/* CSV Operational Report Downloads */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
            <FileSpreadsheet className="w-4 h-4 text-amber-400" />
            <span>Operational CSV Report Exports (§4.10 REQ-1)</span>
          </h3>
          <span className="text-xs text-slate-500 font-mono">Direct Attachment Downloads</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-2.5">
          {[
            { id: 'orders', label: 'Orders CSV' },
            { id: 'shipments', label: 'Shipments CSV' },
            { id: 'inventory', label: 'Inventory CSV' },
            { id: 'suppliers', label: 'Suppliers CSV' },
            { id: 'recommendations', label: 'Recommendations CSV' },
            { id: 'audit', label: 'Audit Log CSV' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => handleDownloadCsv(item.id)}
              className="flex items-center justify-center space-x-1.5 bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 text-xs font-medium py-2.5 px-3 rounded-xl transition-all"
            >
              <Download className="w-3.5 h-3.5 text-indigo-400" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ETL Run History Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200">ETL Pipeline Audit Execution History</h3>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs flex items-center justify-center space-x-2">
            <Activity className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Loading ETL run history...</span>
          </div>
        ) : etlRuns.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No ETL runs recorded. Click 'Run Incremental ETL' to execute pipeline.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-3">Run ID</th>
                  <th className="py-3 px-3">Seed</th>
                  <th className="py-3 px-3">Raw File</th>
                  <th className="py-3 px-3">Loaded</th>
                  <th className="py-3 px-3">Rejected</th>
                  <th className="py-3 px-3">Flagged</th>
                  <th className="py-3 px-3">Duration (s)</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {etlRuns.map((r) => (
                  <tr key={r.run_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 text-indigo-400 font-bold">#{r.run_id}</td>
                    <td className="py-3 px-3">{r.seed}</td>
                    <td className="py-3 px-3 text-slate-400">{r.raw_file_name}</td>
                    <td className="py-3 px-3 text-emerald-400 font-semibold">{r.loaded_records?.toLocaleString()}</td>
                    <td className="py-3 px-3 text-rose-400">{r.rejected_records}</td>
                    <td className="py-3 px-3 text-amber-400">{r.flagged_records}</td>
                    <td className="py-3 px-3">{r.duration_seconds} s</td>
                    <td className="py-3 px-3">
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] px-2 py-0.5 rounded-full uppercase">
                        {r.status || 'completed'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-500 text-[11px]">
                      {r.created_at ? new Date(r.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
