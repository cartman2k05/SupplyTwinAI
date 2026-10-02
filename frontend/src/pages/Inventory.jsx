import React, { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { PackageSearch, AlertTriangle } from 'lucide-react';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataApi.getInventory(50)
      .then((data) => setInventory(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Warehouse Inventory & Stock Control</h1>
          <p className="text-xs text-slate-400">Stock levels on hand, reorder points, and daily demand velocity.</p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <PackageSearch className="w-4 h-4 text-emerald-400" />
          <span className="text-slate-300 font-mono">Stock Records: {inventory.length}</span>
        </div>
      </div>

      <div className="glass-card rounded-xl p-5">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading inventory telemetry...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800 bg-slate-900/50">
                <tr>
                  <th className="py-2.5 px-3">Global ID</th>
                  <th className="py-2.5 px-3">Warehouse Region</th>
                  <th className="py-2.5 px-3">Product ID</th>
                  <th className="py-2.5 px-3">Stock On Hand</th>
                  <th className="py-2.5 px-3">Reorder Point</th>
                  <th className="py-2.5 px-3">Avg Daily Demand</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-300">
                {inventory.map((inv) => {
                  const isLow = inv.stock <= inv.reorder_point;
                  return (
                    <tr key={inv.inventory_id} className="hover:bg-slate-900/50 transition-colors">
                      <td className="py-3 px-3 font-mono font-medium text-emerald-400">{inv.global_id}</td>
                      <td className="py-3 px-3">{inv.warehouse_id}</td>
                      <td className="py-3 px-3 font-mono">{inv.product_id}</td>
                      <td className="py-3 px-3 font-mono font-semibold">{inv.stock}</td>
                      <td className="py-3 px-3 font-mono">{inv.reorder_point}</td>
                      <td className="py-3 px-3 font-mono">{inv.avg_daily_demand}/day</td>
                      <td className="py-3 px-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                          isLow ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}>
                          {isLow ? 'REORDER ALERT' : 'HEALTHY'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
