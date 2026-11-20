import React from 'react';
import { ShieldCheck, Cpu, Terminal, CheckCircle2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer role="contentinfo" aria-label="Site footer" className="border-t border-slate-900 bg-slate-950 py-10 px-4 sm:px-6 lg:px-8 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-900/40 border border-indigo-700/50 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <span className="font-bold text-white tracking-tight">VeriScope AI</span>
            <p className="text-xs text-slate-400">Autonomous Multi-Agent Fact-Checking Engine</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400">
          <span className="flex items-center space-x-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Problem Statement PS03</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>7 Specialized Agents</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            <span>PromptWars x Agent X 2.0</span>
          </span>
        </div>

        <div className="text-xs text-slate-400">
          Built for Hack2skill PromptWars 2026. Non-hallucinatory AI architecture.
        </div>
      </div>
    </footer>
  );
};
