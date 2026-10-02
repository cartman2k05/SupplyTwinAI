import React, { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { Users, ShieldCheck, Star } from 'lucide-react';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataApi.getSuppliers(50)
      .then((data) => setSuppliers(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Supplier Intelligence & Performance</h1>
          <p className="text-xs text-slate-400">Primary category suppliers and alternate re-sourcing candidates.</p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <Users className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-mono">Suppliers Pool: {suppliers.length}</span>
        </div>
      </div>

      <div className="glass-card rounded-xl p-5">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading suppliers telemetry...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800 bg-slate-900/50">
                <tr>
                  <th className="py-2.5 px-3">Global ID</th>
                  <th className="py-2.5 px-3">Supplier Name</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">On-Time Rate</th>
                  <th className="py-2.5 px-3">Defect Rate</th>
                  <th className="py-2.5 px-3">Lead Time</th>
                  <th className="py-2.5 px-3 text-right">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-300">
                {suppliers.map((sup) => (
                  <tr key={sup.supplier_id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3 px-3 font-mono font-medium text-indigo-400">{sup.global_id}</td>
                    <td className="py-3 px-3 font-medium text-white">{sup.name}</td>
                    <td className="py-3 px-3">{sup.category}</td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                        sup.is_primary ? 'bg-indigo-950 text-indigo-300 border border-indigo-800' : 'bg-slate-900 text-slate-400 border border-slate-800'
                      }`}>
                        {sup.is_primary ? 'PRIMARY' : 'ALTERNATE'}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-emerald-400">{(sup.on_time_rate * 100).toFixed(1)}%</td>
                    <td className="py-3 px-3 font-mono text-rose-400">{(sup.defect_rate * 100).toFixed(2)}%</td>
                    <td className="py-3 px-3 font-mono">{sup.lead_time_days} days</td>
                    <td className="py-3 px-3 text-right font-mono text-amber-400 flex items-center justify-end space-x-1">
                      <span>{sup.rating}</span>
                      <Star className="w-3 h-3 fill-amber-400 text-amber-400 inline" />
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
