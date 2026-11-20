import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  ArrowLeft,
  Compass,
  Database,
  FileText,
  ShieldCheck,
  Scale
} from 'lucide-react';
import { api } from '../services/api';
import { AgentExecution } from '../types';

export const AgentActivityPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [agents, setAgents] = useState<AgentExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const agentIcons: Record<string, React.ElementType> = {
    'Research Planner': Compass,
    'Research Discovery': Database,
    'Evidence Extraction': FileText,
    'Fact Verification': CheckCircle2,
    'Source Reliability': ShieldCheck,
    'Contradiction Detection': Scale,
    'Report Generation': Cpu,
  };

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api.getSessionAgents(id)
      .then(setAgents)
      .catch((err) => console.error("Error loading agent telemetry:", err))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex items-center space-x-4">
        <Link
          to={`/results/${id}`}
          className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-white">Multi-Agent Execution Telemetry</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Full audit log of autonomous agents, structured outputs, and runtime execution metrics.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400 text-sm">
          Loading agent activity stream...
        </div>
      ) : agents.length === 0 ? (
        <div className="text-center py-20 text-slate-400 text-sm">
          No agent execution logs recorded for this session.
        </div>
      ) : (
        <div className="space-y-4">
          {agents.map((agent) => {
            const Icon = agentIcons[agent.agent_name] || Cpu;
            const isExpanded = expandedAgent === agent.id;

            return (
              <div
                key={agent.id}
                className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4 transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center shrink-0">
                      <Icon className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h2 className="text-base font-bold text-white">{agent.agent_name}</h2>
                        <span className="text-xs font-mono text-slate-400">
                          {agent.execution_time_ms} ms
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">{agent.task_description}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-start sm:self-center">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                        agent.status === 'COMPLETED'
                          ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400'
                          : agent.status === 'RUNNING'
                          ? 'bg-indigo-950/80 border-indigo-500/40 text-indigo-400'
                          : 'bg-rose-950/80 border-rose-500/40 text-rose-400'
                      }`}
                    >
                      {agent.status}
                    </span>

                    <button
                      onClick={() => setExpandedAgent(isExpanded ? null : agent.id)}
                      className="p-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700"
                      aria-label="Toggle telemetry payload"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {agent.output_summary && (
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-mono text-indigo-300">
                    <strong>Summary: </strong>{agent.output_summary}
                  </div>
                )}

                {/* Raw JSON Telemetry */}
                {isExpanded && agent.output_data && (
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      Structured Agent Output Payload
                    </div>
                    <pre className="text-xs font-mono text-slate-300 overflow-x-auto p-3 bg-slate-900 rounded-lg max-h-80">
                      {JSON.stringify(agent.output_data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
