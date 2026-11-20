import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Search, 
  ArrowRight, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  Scale, 
  AlertTriangle,
  FileText, 
  Database, 
  GitBranch,
  Sparkles,
  Zap,
  Lock,
  Compass
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchMode } from '../types';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<ResearchMode>('demo');
  const [loading, setLoading] = useState(false);

  const sampleQueries = [
    "Is artificial intelligence improving employment opportunities for fresh graduates in India?",
    "Does remote work decrease corporate productivity according to empirical studies?",
    "Are lithium-iron-phosphate (LFP) batteries safer than nickel-manganese-cobalt (NMC) cells?",
  ];

  const handleStartResearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || query.length < 5 || loading) return;

    setLoading(true);
    try {
      const session = await api.startResearch(query.trim(), mode);
      navigate(`/workspace?session=${session.id}`);
    } catch (err) {
      console.error("Failed to initiate research session:", err);
      // Fallback redirect to workspace
      navigate('/workspace');
    } finally {
      setLoading(false);
    }
  };

  const agents = [
    { id: 1, name: 'Research Planner', role: 'Decomposes complex query into 3-5 sub-questions & search targets.', icon: Compass },
    { id: 2, name: 'Research Discovery', role: 'Retrieves external sources, filters spam & eliminates duplicates.', icon: Database },
    { id: 3, name: 'Evidence Extraction', role: 'Extracts discrete claims & statistical facts with citation IDs.', icon: FileText },
    { id: 4, name: 'Fact Verification', role: 'Cross-verifies claims against independent sources (Supported/Contradicted).', icon: CheckCircle2 },
    { id: 5, name: 'Source Reliability', role: 'Evaluates institutional credibility, domain trust & publication freshness.', icon: ShieldCheck },
    { id: 6, name: 'Contradiction Detection', role: 'Diagnoses metric divergences by date, definition & survey population.', icon: Scale },
    { id: 7, name: 'Report Generation', role: 'Synthesizes an 11-section research dossier with transparent citations.', icon: Cpu },
  ];

  return (
    <div className="space-y-24 py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-semibold tracking-wide">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>PromptWars x Agent X 2.0 • Problem Statement PS03</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white max-w-4xl mx-auto leading-tight sm:leading-none">
          Research Smarter. <br />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-cyan-300 bg-clip-text text-transparent">
            Verify Better.
          </span>
        </h1>

        <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          A genuine multi-agent research platform. VeriScope AI coordinates 7 specialized AI agents to independently collect evidence, extract claims, detect source contradictions, and generate transparent research reports.
        </p>

        {/* Research Input Box */}
        <div className="max-w-3xl mx-auto mt-8">
          <form 
            onSubmit={handleStartResearch} 
            className="p-2 sm:p-2.5 bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl shadow-indigo-950/40 focus-within:border-indigo-500/80 transition-all"
          >
            <div className="flex flex-col sm:flex-row items-center gap-2">
              <div className="flex-1 flex items-center px-3 w-full">
                <Search className="w-5 h-5 text-slate-400 shrink-0 mr-3" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask any research question (e.g. AI employment in India...)"
                  className="w-full bg-transparent border-0 text-white placeholder-slate-400 focus:outline-none focus:ring-0 text-sm sm:text-base py-2"
                  maxLength={500}
                  aria-label="Research Question"
                  required
                />
              </div>

              {/* Mode Selector */}
              <div className="flex items-center space-x-2 w-full sm:w-auto px-2 justify-between sm:justify-start">
                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                  <button
                    type="button"
                    onClick={() => setMode('demo')}
                    className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                      mode === 'demo'
                        ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Demo Mode
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('live')}
                    className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                      mode === 'live'
                        ? 'bg-indigo-600 text-white font-bold shadow'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Live Mode
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={loading || query.trim().length < 5}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-400 text-white font-semibold rounded-xl flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/30 transition-all shrink-0 cursor-pointer"
                >
                  {loading ? (
                    <span className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Investigate</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {/* Quick Prompts */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-400">
            <span className="text-slate-400 font-medium">Try asking:</span>
            {sampleQueries.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuery(q)}
                className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 transition-colors text-left truncate max-w-xs"
              >
                "{q.slice(0, 45)}..."
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Multi-Agent Architecture Visualization */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            7 Specialized Autonomous Agents
          </h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Not a single prompt chatbot. Each agent executes a distinct responsibility with validated Pydantic data contracts.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <div 
                key={agent.id}
                className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition-all hover:-translate-y-1 group"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="w-5 h-5 text-indigo-400" />
                  </div>
                  <span className="text-xs font-mono font-bold text-slate-400">Agent {agent.id}</span>
                </div>
                <h3 className="text-base font-bold text-white mb-1.5">{agent.name}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{agent.role}</p>
              </div>
            );
          })}

          {/* Result card */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-950/60 to-purple-950/60 border border-indigo-700/50 flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center mb-4">
                <Zap className="w-5 h-5 text-cyan-300" />
              </div>
              <h3 className="text-base font-bold text-white mb-1">Synthesized Dossier</h3>
              <p className="text-xs text-indigo-200/80 leading-relaxed">
                11-section comprehensive report with verified claims, resolved contradictions, and direct source citations.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-indigo-800/40 flex items-center text-xs text-indigo-300 font-semibold">
              <span>Zero Hallucinations Guarantee</span>
            </div>
          </div>
        </div>
      </section>

      {/* Differentiation Matrix: VeriScope vs LLM Chatbots */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Why VeriScope AI is Different</h2>
          <p className="text-sm text-slate-400">Comparing typical single-prompt AI with VeriScope's multi-agent pipeline</p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/80 text-xs font-semibold text-slate-300 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Feature</th>
                <th className="p-4 text-slate-400">Standard AI Chatbot</th>
                <th className="p-4 text-indigo-400 font-bold">VeriScope AI (PS03)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr>
                <td className="p-4 font-medium text-white">Source Hallucination</td>
                <td className="p-4 text-rose-400 flex items-center gap-1.5">
                  <XCircle className="w-4 h-4 shrink-0" />
                  <span>Frequently fabricates papers, URLs & dates</span>
                </td>
                <td className="p-4 text-emerald-400 font-medium">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>Real retrieved URLs, SSRF filtered & deduplicated</span>
                  </span>
                </td>
              </tr>
              <tr>
                <td className="p-4 font-medium text-white">Claim Verification</td>
                <td className="p-4 text-slate-400">Uncalibrated generative confidence</td>
                <td className="p-4 text-indigo-300 font-medium">5-stage epistemic taxonomy (Supported to Contradicted)</td>
              </tr>
              <tr>
                <td className="p-4 font-medium text-white">Contradiction Diagnosis</td>
                <td className="p-4 text-slate-400">Smooths over disagreements or hallucinates one</td>
                <td className="p-4 text-indigo-300 font-medium">Analyzes date, sample population & definition nuances</td>
              </tr>
              <tr>
                <td className="p-4 font-medium text-white">Security & Sandboxing</td>
                <td className="p-4 text-slate-400">Vulnerable to web-based prompt injections</td>
                <td className="p-4 text-indigo-300 font-medium">SSRF blocking, input sanitization & instruction isolation</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
