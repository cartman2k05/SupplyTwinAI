import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function DelayChart({ modeData }) {
  const labels = ['First Class', 'Second Class', 'Same Day', 'Standard Class'];
  const defaultValues = [2.4, 1.8, 0.9, 0.4];

  const data = {
    labels,
    datasets: [
      {
        label: 'Avg Delay (Days)',
        data: modeData || defaultValues,
        backgroundColor: '#3b82f6',
        borderRadius: 6,
        hoverBackgroundColor: '#60a5fa',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#94a3b8', font: { size: 10 } },
      },
      y: {
        grid: { color: '#1e293b' },
        ticks: { color: '#94a3b8', font: { size: 10 } },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="glass-card rounded-xl p-5 flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Delay by Shipping Mode</h3>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
          Empirical DataCo
        </span>
      </div>
      <div className="flex-1 min-h-[180px]">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}
