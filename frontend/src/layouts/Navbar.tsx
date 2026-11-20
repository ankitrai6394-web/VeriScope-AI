import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ShieldCheck, 
  Search, 
  History, 
  Settings as SettingsIcon, 
  Cpu, 
  Activity,
  ExternalLink 
} from 'lucide-react';
import { api } from '../services/api';
import { HealthInfo } from '../types';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [health, setHealth] = useState<HealthInfo | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const navLinks = [
    { path: '/workspace', label: 'Workspace', icon: Search },
    { path: '/history', label: 'Research History', icon: History },
    { path: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/30 transition-all">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                  VeriScope<span className="text-indigo-400">.AI</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded">
                  PS03
                </span>
              </div>
              <p className="text-[10px] text-slate-400 -mt-0.5">Multi-Agent Verification</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1" role="navigation" aria-label="Main navigation">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800/80 text-indigo-300 border border-slate-700/60 shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Status & Operational Mode Pill */}
          <div className="flex items-center space-x-3">
            {health && (
              <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-full text-xs font-mono border border-slate-800 bg-slate-900/80">
                <span className={`w-2 h-2 rounded-full ${health.live_mode_available ? 'bg-emerald-400 animate-pulse' : 'bg-cyan-400'}`} />
                <span className="text-slate-300">
                  {health.live_mode_available ? 'Live Ready' : 'Verified Demo Mode'}
                </span>
              </div>
            )}

            <Link
              to="/workspace"
              className="hidden lg:inline-flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Cpu className="w-4 h-4" />
              <span>Launch Research</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};
