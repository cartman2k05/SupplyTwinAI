import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function RiskChart({ lowCount = 38, medCount = 12, highCount = 4 }) {
  const data = {
    labels: ['Low Risk (< 33)', 'Medium Risk (33–66)', 'High Risk (> 66)'],
    datasets: [
      {
        data: [lowCount, medCount, highCount],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: ['#047857', '#b45309', '#b91c1c'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',
          font: { size: 11 },
          padding: 12,
        },
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
    cutout: '70%',
  };

  return (
    <div className="glass-card rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Risk Distribution</h3>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
          Composite Score
        </span>
      </div>
      <div className="relative flex-1 min-h-[180px] flex items-center justify-center">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
}
