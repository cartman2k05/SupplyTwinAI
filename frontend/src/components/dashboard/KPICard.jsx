import React from 'react';

export default function KPICard({ title, value, subtext, icon: Icon, color = 'indigo', trend }) {
  const colorMap = {
    indigo: 'text-indigo-400 border-indigo-500/20 bg-indigo-500/10',
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
    amber: 'text-amber-400 border-amber-500/20 bg-amber-500/10',
    rose: 'text-rose-400 border-rose-500/20 bg-rose-500/10',
  };

  return (
    <div className="glass-card rounded-xl p-5 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${colorMap[color] || colorMap.indigo}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div>
        <div className="text-2xl font-bold tracking-tight text-white">{value}</div>
        <div className="flex items-center justify-between mt-1 text-xs">
          <span className="text-slate-400">{subtext}</span>
          {trend && (
            <span className={trend.positive ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-semibold'}>
              {trend.label}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
