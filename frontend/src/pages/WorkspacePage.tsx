import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { 
  Search, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertCircle, 
  ArrowRight,
  Database,
  FileText,
  ShieldCheck,
  Scale,
  Compass,
  Play,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchMode, ResearchSession } from '../types';

export const WorkspacePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<ResearchMode>('demo');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(searchParams.get('session'));
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [recentSessions, setRecentSessions] = useState<ResearchSession[]>([]);

  // Agent Icon Mapping
  const agentIcons: Record<string, React.ElementType> = {
    'Research Planner': Compass,
    'Research Discovery': Database,
    'Evidence Extraction': FileText,
    'Fact Verification': CheckCircle2,
    'Source Reliability': ShieldCheck,
    'Contradiction Detection': Scale,
    'Report Generation': Cpu,
  };

  // Load recent sessions
  const fetchRecentSessions = () => {
    api.getHistory(0, 5)
      .then(setRecentSessions)
      .catch((err) => console.error("Error loading recent sessions:", err));
  };

  useEffect(() => {
    fetchRecentSessions();
  }, []);

  // Handle active session polling
  useEffect(() => {
    if (!activeSessionId) return;

    let isSubscribed = true;
    const interval = setInterval(async () => {
      try {
        const data = await api.getSessionStatus(activeSessionId);
        if (!isSubscribed) return;
        setSessionData(data);

        // If completed or failed, stop polling
        if (data.status === 'COMPLETED' || data.status === 'FAILED') {
          clearInterval(interval);
          fetchRecentSessions();
        }
      } catch (err) {
        console.error("Error polling session status:", err);
      }
    }, 1500);

    return () => {
      isSubscribed = false;
      clearInterval(interval);
    };
  }, [activeSessionId]);

  const handleStartResearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || query.length < 5 || loading) return;

    setLoading(true);
    try {
      const session = await api.startResearch(query.trim(), mode);
      setActiveSessionId(session.id);
      setSessionData({
        id: session.id,
        query: session.query,
        mode: session.mode,
        status: 'RUNNING',
        agents: [],
      });
      fetchRecentSessions();
    } catch (err) {
      console.error("Failed to start research:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span aria-label="Status: Completed" className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-500/40">
            <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Completed</span>
          </span>
        );
      case 'RUNNING':
        return (
          <span aria-label="Status: Running" className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950/80 text-indigo-400 border border-indigo-500/40 animate-pulse">
            <RotateCcw className="w-3.5 h-3.5 animate-spin" aria-hidden="true" />
            <span>Running</span>
          </span>
        );
      case 'FAILED':
        return (
          <span aria-label="Status: Failed" className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-500/40">
            <XCircle className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Failed</span>
          </span>
        );
      case 'PENDING':
      default:
        return (
          <span aria-label="Status: Pending" className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-700">
            <Clock className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Pending</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center space-x-3">
            <span>Research Workspace</span>
            <span className="px-2 py-0.5 text-xs font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded">
              Multi-Agent Orchestration
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Dispatch queries across the 7 autonomous agents. Track real-time execution telemetry and evidence aggregation.
          </p>
        </div>

        {activeSessionId && sessionData?.status === 'COMPLETED' && (
          <button
            onClick={() => navigate(`/results/${activeSessionId}`)}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl font-bold text-sm bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 cursor-pointer"
          >
            <span>View Full Dossier</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Input Form & Recents */}
        <div className="space-y-6 lg:col-span-1">
          {/* Form Card */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-xl space-y-5">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Compass className="w-4 h-4 text-indigo-400" />
              <span>Initiate Investigation</span>
            </h2>

            <form onSubmit={handleStartResearch} className="space-y-4" aria-label="Research investigation form">
              <div>
                <label htmlFor="query-input" className="block text-xs font-semibold text-slate-400 mb-1">
                  Research Question / Topic
                </label>
                <textarea
                  id="query-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter a factual or empirical question..."
                  rows={4}
                  maxLength={500}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors resize-none"
                  required
                  aria-describedby="query-hint"
                />
                <div id="query-hint" className="flex justify-between items-center text-[11px] text-slate-400 mt-1">
                  <span>Minimum 5 characters</span>
                  <span aria-live="polite" aria-atomic="true">{query.length} / 500</span>
                </div>
              </div>

              {/* Mode Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-2" id="mode-label">
                  Execution Mode
                </label>
                <div className="grid grid-cols-2 gap-2" role="group" aria-labelledby="mode-label">
                  <button
                    type="button"
                    onClick={() => setMode('demo')}
                    aria-pressed={mode === 'demo'}
                    className={`p-2.5 rounded-xl border text-xs font-medium text-left transition-all ${
                      mode === 'demo'
                        ? 'border-cyan-500/80 bg-cyan-950/40 text-cyan-300'
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-bold flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-cyan-400" aria-hidden="true" />
                      <span>Verified Demo</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1">
                      Deterministic real data. No API keys needed.
                    </p>
                  </button>

                  <button
                    type="button"
                    onClick={() => setMode('live')}
                    aria-pressed={mode === 'live'}
                    className={`p-2.5 rounded-xl border text-xs font-medium text-left transition-all ${
                      mode === 'live'
                        ? 'border-indigo-500/80 bg-indigo-950/40 text-indigo-300'
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="font-bold flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-indigo-400" aria-hidden="true" />
                      <span>Live Search</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-1">
                      Tavily Search + LLM live execution.
                    </p>
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || query.trim().length < 5}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-400 text-white font-bold rounded-xl flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
              >
                {loading ? (
                  <RotateCcw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-white" />
                    <span>Run Multi-Agent Pipeline</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Recent Investigations */}
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Recent Research Sessions
            </h3>
            <div className="space-y-2">
              {recentSessions.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No past sessions found.</p>
              ) : (
                recentSessions.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => {
                      setActiveSessionId(s.id);
                      setSessionData(null);
                    }}
                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                      activeSessionId === s.id
                        ? 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200'
                        : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="text-xs font-semibold truncate">{s.query}</div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1.5">
                      <span className="capitalize">{s.mode} Mode</span>
                      <span className={s.status === 'COMPLETED' ? 'text-emerald-400' : 'text-slate-400'}>
                        {s.status}
                      </span>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Multi-Agent Execution Telemetry */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Cpu className="w-5 h-5 text-indigo-400" />
                  <span>Agent Execution Pipeline</span>
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Live asynchronous tracking of all 7 specialized agents.
                </p>
              </div>

              {sessionData && (
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono text-slate-400">
                    Status:
                  </span>
                  {getStatusBadge(sessionData.status)}
                </div>
              )}
            </div>

            {/* If no active session */}
            {!activeSessionId && !sessionData && (
              <div className="text-center py-16 space-y-4">
                <div className="w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <Search className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">No Active Session Selected</h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                    Enter a research question in the form on the left or select a previous session to inspect agent telemetry.
                  </p>
                </div>
              </div>
            )}

            {/* Active Session Display */}
            {sessionData && (
              <div className="space-y-6">
                {/* Session Query Card */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Active Research Target
                  </div>
                  <div className="text-sm font-semibold text-white">
                    "{sessionData.query}"
                  </div>
                  <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400 font-mono">
                    <span>Sources: <strong className="text-indigo-400">{sessionData.total_sources || 0}</strong></span>
                    <span>Claims: <strong className="text-indigo-400">{sessionData.total_claims || 0}</strong></span>
                    <span>Verified: <strong className="text-emerald-400">{sessionData.verified_claims || 0}</strong></span>
                    <span>Contradicted: <strong className="text-rose-400">{sessionData.contradicted_claims || 0}</strong></span>
                  </div>
                </div>

                {/* Agent Execution List */}
                <div className="space-y-3">
                  {sessionData.agents && sessionData.agents.length > 0 ? (
                    sessionData.agents.map((agent: any, index: number) => {
                      const Icon = agentIcons[agent.agent_name] || Cpu;
                      return (
                        <div
                          key={index}
                          className="p-4 rounded-xl bg-slate-950 border border-slate-800/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
                        >
                          <div className="flex items-start space-x-3">
                            <div className="w-9 h-9 rounded-lg bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center shrink-0 mt-0.5">
                              <Icon className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm font-bold text-white">{agent.agent_name}</span>
                                {agent.execution_time_ms > 0 && (
                                  <span className="text-[10px] font-mono text-slate-400">
                                    {agent.execution_time_ms}ms
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-slate-400 mt-0.5">{agent.task_description}</p>
                              {agent.output_summary && (
                                <div className="mt-2 inline-block px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] text-indigo-300 font-mono">
                                  {agent.output_summary}
                                </div>
                              )}
                              {agent.error_message && (
                                <div className="mt-2 text-xs text-rose-400 font-mono">
                                  {agent.error_message}
                                </div>
                              )}
                            </div>
                          </div>

                          <div className="shrink-0 self-start sm:self-center">
                            {getStatusBadge(agent.status)}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-center py-10 space-y-2" role="status" aria-label="Loading research agents">
                      <RotateCcw className="w-5 h-5 text-indigo-400 animate-spin mx-auto" aria-hidden="true" />
                      <p className="text-xs text-slate-400">Spinning up research planner & agent network...</p>
                    </div>
                  )}
                </div>

                {/* Completion Action Banner */}
                {sessionData.status === 'COMPLETED' && (
                  <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/80 to-slate-900 border border-indigo-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <div className="text-sm font-bold text-white">Investigation Complete</div>
                        <div className="text-xs text-slate-400">All claims extracted, cross-verified, and synthesized.</div>
                      </div>
                    </div>

                    <button
                      onClick={() => navigate(`/results/${sessionData.id}`)}
                      className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/30 transition-all cursor-pointer"
                    >
                      <span>Explore Report & Visualizations</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
