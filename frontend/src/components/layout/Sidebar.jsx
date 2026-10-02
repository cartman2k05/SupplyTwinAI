import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Truck,
  PackageSearch,
  Users,
  Network,
  Bot,
  Lightbulb,
  Settings,
  Database
} from 'lucide-react';

export default function Sidebar() {
  const { role } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Shipments', path: '/shipments', icon: Truck },
    { name: 'Inventory', path: '/inventory', icon: PackageSearch },
    { name: 'Suppliers', path: '/suppliers', icon: Users },
    { name: 'Digital Twin Graph', path: '/graph', icon: Network, badge: 'Phase 5' },
    { name: 'AI Assistant', path: '/chat', icon: Bot, badge: 'Phase 6' },
    { name: 'Recommendations', path: '/recommendations', icon: Lightbulb, badge: 'Phase 8' },
  ];

  const adminItems = [
    { name: 'Admin Configuration', path: '/admin/config', icon: Settings },
    { name: 'ETL Audit Manager', path: '/admin/etl', icon: Database },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        <div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
            Operations Center
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-mono text-slate-500 bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Admin Navigation Section - Strictly Hidden for Manager Role (§4.2 REQ-2) */}
        {role === 'admin' && (
          <div>
            <div className="text-[11px] font-semibold text-amber-500/80 uppercase tracking-wider px-3 mb-2">
              System Administration
            </div>
            <nav className="space-y-1">
              {adminItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    }`
                  }
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-900 text-xs text-slate-500 text-center font-mono">
        SupplyTwinAI Capstone • Team 12
      </div>
    </aside>
  );
}
