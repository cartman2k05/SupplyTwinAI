import React from 'react';
import { AlertTriangle, Clock, ShieldAlert, ArrowUpRight } from 'lucide-react';

export default function DisruptionsTable({ events = [] }) {
  const sampleEvents = events.length > 0 ? events : [
    {
      id: 'EVT-101',
      global_id: 'supplier:12',
      target: 'Primary Supplier - Caguas',
      type: 'Supplier Delay Cluster',
      severity: 82,
      status: 'HIGH RISK',
      time: '12 mins ago',
    },
    {
      id: 'EVT-102',
      global_id: 'shipment:77202',
      target: 'Shipment #77202 (Standard)',
      type: 'Adverse Weather Route Disrupt',
      severity: 68,
      status: 'MEDIUM RISK',
      time: '45 mins ago',
    },
    {
      id: 'EVT-103',
      global_id: 'inventory:45',
      target: 'Warehouse Europe - Inventory Stockout',
      type: 'Stock Buffer Reorder Alert',
      severity: 62,
      status: 'MEDIUM RISK',
      time: '2 hours ago',
    },
  ];

  return (
    <div className="glass-card rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white">Active Disruption Signals</h3>
        </div>
        <span className="text-xs text-indigo-400 font-medium hover:underline cursor-pointer flex items-center space-x-1">
          <span>View All</span>
          <ArrowUpRight className="w-3 h-3" />
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="text-slate-400 border-b border-slate-800 bg-slate-900/50">
            <tr>
              <th className="py-2.5 px-3">Target Entity</th>
              <th className="py-2.5 px-3">Disruption Type</th>
              <th className="py-2.5 px-3">Severity Score</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3 text-right">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 text-slate-300">
            {sampleEvents.map((evt) => (
              <tr key={evt.id} className="hover:bg-slate-900/50 transition-colors">
                <td className="py-3 px-3 font-medium text-white flex items-center space-x-2">
                  <span className="font-mono text-slate-400">{evt.global_id}</span>
                </td>
                <td className="py-3 px-3">{evt.type}</td>
                <td className="py-3 px-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${evt.severity > 70 ? 'bg-rose-500' : 'bg-amber-500'}`}
                        style={{ width: `${evt.severity}%` }}
                      ></div>
                    </div>
                    <span className="font-mono text-[11px]">{evt.severity}</span>
                  </div>
                </td>
                <td className="py-3 px-3">
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide ${
                      evt.severity > 70
                        ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                        : 'bg-amber-950/80 text-amber-300 border border-amber-800'
                    }`}
                  >
                    {evt.status}
                  </span>
                </td>
                <td className="py-3 px-3 text-right text-slate-400 font-mono text-[11px]">
                  {evt.time}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
