import React, { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { Truck, Clock, AlertTriangle } from 'lucide-react';

export default function Shipments() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataApi.getShipments(50)
      .then((data) => setShipments(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Shipment Tracking & Logistics</h1>
          <p className="text-xs text-slate-400">Order delivery status, transit delays, and routing state.</p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
          <Truck className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-mono">Total Tracked: {shipments.length}</span>
        </div>
      </div>

      <div className="glass-card rounded-xl p-5">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading shipments telemetry...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 border-b border-slate-800 bg-slate-900/50">
                <tr>
                  <th className="py-2.5 px-3">Global ID</th>
                  <th className="py-2.5 px-3">Shipping Mode</th>
                  <th className="py-2.5 px-3">Scheduled Days</th>
                  <th className="py-2.5 px-3">Real Days</th>
                  <th className="py-2.5 px-3">Delivery Status</th>
                  <th className="py-2.5 px-3">Simulated State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-300">
                {shipments.map((shipment) => (
                  <tr key={shipment.shipment_id} className="hover:bg-slate-900/50 transition-colors">
                    <td className="py-3 px-3 font-mono font-medium text-indigo-400">{shipment.global_id}</td>
                    <td className="py-3 px-3">{shipment.shipping_mode}</td>
                    <td className="py-3 px-3 font-mono">{shipment.days_scheduled}d</td>
                    <td className="py-3 px-3 font-mono">{shipment.days_real}d</td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                        shipment.delivery_status === 'Late delivery' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}>
                        {shipment.delivery_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-500">
                      {shipment.is_simulated ? 'SIMULATED' : 'HISTORICAL'}
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
