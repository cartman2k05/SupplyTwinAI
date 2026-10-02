import React, { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { Settings, Save, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function AdminConfig() {
  const [config, setConfig] = useState({
    risk_weight_supplier: 0.30,
    risk_weight_shipment: 0.30,
    risk_weight_inventory: 0.20,
    risk_weight_external: 0.20,
    threshold_low_medium: 33.0,
    threshold_medium_high: 66.0,
    alert_threshold_recommendation: 60.0,
  });

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    dataApi.getAdminConfig()
      .then((data) => setConfig(data))
      .catch((err) => setError(err.message || 'Failed to load configuration'))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (field, value) => {
    setConfig((prev) => ({
      ...prev,
      [field]: parseFloat(value) || 0,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    const sum =
      config.risk_weight_supplier +
      config.risk_weight_shipment +
      config.risk_weight_inventory +
      config.risk_weight_external;

    if (Math.abs(sum - 1.0) > 0.01) {
      setError(`Risk weights must sum to 1.0 (current sum: ${sum.toFixed(2)})`);
      return;
    }

    try {
      const updated = await dataApi.updateAdminConfig(config);
      setConfig(updated);
      setMessage('Configuration updated successfully!');
    } catch (err) {
      setError(err.message || 'Update failed');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Settings className="w-5 h-5 text-amber-400" />
          <span>System & Agent Risk Configuration</span>
        </h1>
        <p className="text-xs text-slate-400">
          Editable risk scoring weights, alert thresholds, and recommendation triggers (§4.9 REQ-2).
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-950/80 border border-rose-800 rounded-lg flex items-center space-x-2 text-xs text-rose-200">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {message && (
        <div className="p-3 bg-emerald-950/80 border border-emerald-800 rounded-lg flex items-center space-x-2 text-xs text-emerald-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-card rounded-xl p-6 space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-white mb-4 border-b border-slate-800 pb-2">
            Composite Risk Score Weights (Must sum to 1.0)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Supplier Agent Weight</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={config.risk_weight_supplier}
                onChange={(e) => handleChange('risk_weight_supplier', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Shipment Agent Weight</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={config.risk_weight_shipment}
                onChange={(e) => handleChange('risk_weight_shipment', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Inventory Agent Weight</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={config.risk_weight_inventory}
                onChange={(e) => handleChange('risk_weight_inventory', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">External Intelligence Weight</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={config.risk_weight_external}
                onChange={(e) => handleChange('risk_weight_external', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-white mb-4 border-b border-slate-800 pb-2">
            Risk Score Bands & Recommendation Alert Triggers
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Low / Medium Threshold</label>
              <input
                type="number"
                value={config.threshold_low_medium}
                onChange={(e) => handleChange('threshold_low_medium', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Medium / High Threshold</label>
              <input
                type="number"
                value={config.threshold_medium_high}
                onChange={(e) => handleChange('threshold_medium_high', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Recommendation Alert Trigger</label>
              <input
                type="number"
                value={config.alert_threshold_recommendation}
                onChange={(e) => handleChange('alert_threshold_recommendation', e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm font-mono text-white"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="bg-amber-600 hover:bg-amber-500 text-white font-medium px-5 py-2.5 rounded-lg flex items-center space-x-2 transition-all"
        >
          <Save className="w-4 h-4" />
          <span>Save System Configuration</span>
        </button>
      </form>
    </div>
  );
}
