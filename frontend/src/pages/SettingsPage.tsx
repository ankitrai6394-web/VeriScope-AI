import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  ShieldCheck, 
  Cpu, 
  Database, 
  Lock, 
  CheckCircle2, 
  AlertTriangle,
  Key,
  Sliders,
  Server
} from 'lucide-react';
import { api } from '../services/api';
import { HealthInfo } from '../types';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch((err) => console.error("Error loading settings:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="border-b border-slate-800 pb-6">
        <h1 className="text-3xl font-extrabold text-white flex items-center space-x-3">
          <SettingsIcon className="w-7 h-7 text-indigo-400" />
          <span>System & Security Settings</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Diagnostics, provider integrations, and security guardrails governing VeriScope AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* LLM Provider Status Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">LLM Provider</h2>
                <p className="text-xs text-slate-400">Structured JSON Reasoning Engine</p>
              </div>
            </div>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
              health?.providers.llm.configured
                ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-400'
            }`}>
              {health?.providers.llm.configured ? 'Live API Key Set' : 'Deterministic Mock Active'}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Active Provider:</span>
              <span className="text-white font-bold">{health?.providers.llm.provider || 'gemini'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Configured Model:</span>
              <span className="text-indigo-400 font-bold">{health?.providers.llm.model || 'gemini-1.5-flash'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Response Mode:</span>
              <span className="text-slate-300">Pydantic JSON Enforced</span>
            </div>
          </div>
          <p className="text-xs text-slate-400">
            To switch to a live Gemini or OpenAI key, configure <code className="text-indigo-300">LLM_API_KEY</code> in <code className="text-indigo-300">.env</code>.
          </p>
        </div>

        {/* Search Provider Status Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center">
                <Database className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Search Provider</h2>
                <p className="text-xs text-slate-400">Web Evidence Retrieval</p>
              </div>
            </div>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
              health?.providers.search.configured
                ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-400'
            }`}>
              {health?.providers.search.configured ? 'Tavily Key Active' : 'Deterministic Mock Active'}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Search Engine:</span>
              <span className="text-white font-bold">{health?.providers.search.provider || 'tavily'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Max Results/Query:</span>
              <span className="text-cyan-400 font-bold">5 sources</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Deduplication:</span>
              <span className="text-emerald-400 font-bold">Enabled (Canonical URL)</span>
            </div>
          </div>
          <p className="text-xs text-slate-400">
            Configure <code className="text-indigo-300">SEARCH_API_KEY</code> in <code className="text-indigo-300">.env</code> to activate live external web search.
          </p>
        </div>
      </div>

      {/* Security Architecture Card */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Hardened Security Guardrails</h2>
            <p className="text-xs text-slate-400">Multi-tier safeguards protecting agents from malicious web content.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="font-bold text-white flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>SSRF Protection</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Blocks RFC 1918 private IPs (10.x, 172.16.x, 192.168.x), loopbacks, and cloud metadata services.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="font-bold text-white flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Prompt Sandboxing</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Isolates retrieved web text from system instructions, neutralizing injected instructions.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="font-bold text-white flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>Input Capping</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Enforces a strict 500-character cap on incoming queries to prevent prompt bloat & buffer misuse.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="font-bold text-white flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-indigo-400" />
              <span>Secret Masking</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Zero API credentials or system paths exposed to frontend clients or persisted in SQLite.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
