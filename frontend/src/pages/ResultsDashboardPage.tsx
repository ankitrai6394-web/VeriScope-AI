import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Scale, 
  HelpCircle,
  ExternalLink, 
  FileText, 
  Layers, 
  Copy, 
  Check, 
  Download,
  Database,
  Calendar,
  Share2,
  ChevronDown,
  ChevronUp,
  Cpu
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as RechartsTooltip, 
  Legend, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid 
} from 'recharts';
import { api } from '../services/api';
import { ResearchSessionDetail, VerificationStatus } from '../types';
import { getVerificationBadge, formatDate } from '../utils/format';

export const ResultsDashboardPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<ResearchSessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'claims' | 'contradictions' | 'sources' | 'report'>('claims');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [copied, setCopied] = useState(false);
  const [expandedClaim, setExpandedClaim] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api.getSessionDetail(id)
      .then((data) => {
        setSession(data);
        setError(null);
      })
      .catch((err) => {
        console.error("Error loading session:", err);
        setError("Failed to load research session results.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto" />
        <p className="text-sm text-slate-400">Loading research dossier and verification data...</p>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-24 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-rose-950/60 border border-rose-800/40 flex items-center justify-center mx-auto text-rose-400">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Dossier Unavailable</h2>
        <p className="text-sm text-slate-400">{error || "Research session not found."}</p>
        <Link
          to="/workspace"
          className="inline-flex px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
        >
          Return to Workspace
        </Link>
      </div>
    );
  }

  // Chart data
  const chartData = [
    { name: 'Supported', value: session.verified_claims, color: '#10b981' },
    { name: 'Contradicted', value: session.contradicted_claims, color: '#f43f5e' },
    { name: 'Partially Supported', value: session.partially_supported_claims, color: '#f59e0b' },
    { name: 'Conflicting', value: session.conflicting_claims, color: '#a855f7' },
    { name: 'Insufficient', value: session.insufficient_claims, color: '#64748b' },
  ].filter((d) => d.value > 0);

  // Grouped verifications map
  const verificationMap = new Map();
  session.verifications?.forEach((v) => {
    verificationMap.set(v.claim_id, v);
  });

  // Filtered claims
  const filteredClaims = (session.claims || []).filter((claim) => {
    if (statusFilter === 'ALL') return true;
    const v = verificationMap.get(claim.claim_id);
    return v?.verification_status === statusFilter;
  });

  const handleCopyMarkdown = () => {
    if (!session.report?.markdown_content) return;
    navigator.clipboard.writeText(session.report.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadReport = () => {
    if (!session.report?.markdown_content) return;
    const blob = new Blob([session.report.markdown_content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veriscope-report-${session.id.slice(0, 8)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Overview Header */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="space-y-2 max-w-4xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {session.mode} Research Session
              </span>
              <span className="text-xs text-slate-400">
                Completed on {formatDate(session.updated_at)}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white leading-snug">
              {session.query}
            </h1>
          </div>

          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleCopyMarkdown}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-1.5 border border-slate-700 transition-colors cursor-pointer"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied' : 'Copy Report'}</span>
            </button>
            <button
              onClick={handleDownloadReport}
              className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Export .MD</span>
            </button>
          </div>
        </div>

        {/* Metric Cards Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <div className="text-[11px] font-semibold text-slate-400 uppercase">Sources</div>
            <div className="text-2xl font-black text-white mt-1">{session.total_sources}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <div className="text-[11px] font-semibold text-slate-400 uppercase">Claims</div>
            <div className="text-2xl font-black text-indigo-400 mt-1">{session.total_claims}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/40">
            <div className="text-[11px] font-semibold text-emerald-400 uppercase">Supported</div>
            <div className="text-2xl font-black text-emerald-400 mt-1">{session.verified_claims}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-rose-900/40">
            <div className="text-[11px] font-semibold text-rose-400 uppercase">Contradicted</div>
            <div className="text-2xl font-black text-rose-400 mt-1">{session.contradicted_claims}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-purple-900/40">
            <div className="text-[11px] font-semibold text-purple-400 uppercase">Conflicting</div>
            <div className="text-2xl font-black text-purple-400 mt-1">{session.conflicting_claims}</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
            <div className="text-[11px] font-semibold text-slate-400 uppercase">Partial/Insuff</div>
            <div className="text-2xl font-black text-amber-400 mt-1">
              {session.partially_supported_claims + session.insufficient_claims}
            </div>
          </div>
        </div>
      </div>

      {/* Visualizations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Donut Chart: Verification Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span>Verification Distribution</span>
          </h2>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{ backgroundColor: '#020617', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-3 text-xs">
            {chartData.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-1.5 font-medium text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span>{item.name}: <strong>{item.value}</strong></span>
              </div>
            ))}
          </div>
        </div>

        {/* Methodology & Executive Highlights */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2 mb-3">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Executive Synthesis</span>
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              {session.report?.executive_summary || "Multi-agent research synthesis in progress..."}
            </p>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 space-y-2">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Methodology Framework</div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {session.report?.methodology || "Multi-source evidence cross-referencing."}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-800">
        <nav className="flex space-x-4 sm:space-x-8" aria-label="Dossier Tabs">
          {[
            { id: 'claims', label: `Verified Claims (${session.claims?.length || 0})`, icon: CheckCircle2 },
            { id: 'contradictions', label: `Contradiction Analysis (${session.report?.contradiction_analysis?.length || 0})`, icon: Scale },
            { id: 'sources', label: `Source Explorer (${session.sources?.length || 0})`, icon: Database },
            { id: 'report', label: '11-Section Dossier', icon: FileText },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-3 px-1 border-b-2 font-bold text-sm flex items-center space-x-2 transition-all cursor-pointer ${
                  isActive
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* TAB 1: CLAIMS EXPLORER */}
      {activeTab === 'claims' && (
        <div className="space-y-6">
          {/* Status Filter Buttons */}
          <div className="flex flex-wrap gap-2">
            {['ALL', 'SUPPORTED', 'CONTRADICTED', 'PARTIALLY_SUPPORTED', 'CONFLICTING_EVIDENCE', 'INSUFFICIENT_EVIDENCE'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  statusFilter === s
                    ? 'bg-indigo-600 border-indigo-500 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {s.replace(/_/g, ' ')}
              </button>
            ))}
          </div>

          <div className="space-y-4">
            {filteredClaims.map((claim) => {
              const ver = verificationMap.get(claim.claim_id);
              const badge = getVerificationBadge(ver?.verification_status || 'INSUFFICIENT_EVIDENCE');
              const isExpanded = expandedClaim === claim.claim_id;

              return (
                <div
                  key={claim.claim_id}
                  className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-xs font-bold text-indigo-400">
                          {claim.claim_id}
                        </span>
                        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-semibold">
                          {claim.evidence_type}
                        </span>
                        <span className="text-[11px] text-slate-400 font-mono">
                          Confidence: {(claim.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-white leading-snug">
                        {claim.claim_text}
                      </h3>
                    </div>

                    <div className="shrink-0">
                      <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border ${badge.badgeClass}`}>
                        <span>{badge.label}</span>
                      </span>
                    </div>
                  </div>

                  {/* Verification Rationale */}
                  {ver && (
                    <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-2">
                      <p className="text-slate-300 leading-relaxed">
                        <strong className="text-slate-100">Verification Finding: </strong>
                        {ver.explanation}
                      </p>

                      <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                        {ver.supporting_sources?.length > 0 && (
                          <div className="flex items-center space-x-1 text-emerald-400">
                            <span>Supported by:</span>
                            {ver.supporting_sources.map((srcId: string) => (
                              <span key={srcId} className="px-1.5 py-0.5 rounded bg-emerald-950 border border-emerald-800/50 font-mono font-bold">
                                {srcId}
                              </span>
                            ))}
                          </div>
                        )}

                        {ver.contradicting_sources?.length > 0 && (
                          <div className="flex items-center space-x-1 text-rose-400">
                            <span>Contradicted by:</span>
                            {ver.contradicting_sources.map((srcId: string) => (
                              <span key={srcId} className="px-1.5 py-0.5 rounded bg-rose-950 border border-rose-800/50 font-mono font-bold">
                                {srcId}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Expandable Limitations */}
                      {ver.limitations && (
                        <div className="pt-2 border-t border-slate-900 text-slate-400 italic">
                          <span>Limitation: </span>{ver.limitations}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 2: CONTRADICTION ANALYSIS */}
      {activeTab === 'contradictions' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 text-xs text-purple-200">
            <strong>Cross-Source Discrepancy Diagnostics: </strong>
            Rather than blindly declaring one source false, VeriScope AI investigates whether differences stem from publication year, target population, sample definitions, or survey methodologies.
          </div>

          {session.report?.contradiction_analysis && session.report.contradiction_analysis.length > 0 ? (
            session.report.contradiction_analysis.map((c, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Scale className="w-4 h-4 text-purple-400" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Divergence Cause: <span className="text-purple-300 font-mono capitalize">{c.divergence_reason}</span>
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 font-mono text-[11px] text-slate-400">
                    <span>Sources:</span>
                    {c.conflicting_sources.map((s) => (
                      <span key={s} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">{s}</span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-[11px] font-bold text-slate-400 mb-1">Perspective A</div>
                    <div className="text-xs text-slate-200 font-medium">"{c.statement_a}"</div>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-[11px] font-bold text-slate-400 mb-1">Perspective B</div>
                    <div className="text-xs text-slate-200 font-medium">"{c.statement_b}"</div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-800/40 text-xs text-slate-300">
                  <strong className="text-indigo-300">Reconciliation Analysis: </strong>
                  {c.analysis}
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center text-slate-400 text-sm">
              No substantive contradictions detected across independent sources for this inquiry.
            </div>
          )}
        </div>
      )}

      {/* TAB 3: SOURCE EXPLORER */}
      {activeTab === 'sources' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {session.sources?.map((src) => (
            <div
              key={src.source_id}
              className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-3 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                    {src.source_id}
                  </span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {src.source_type}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white line-clamp-2">
                  {src.title}
                </h3>

                <p className="text-xs text-slate-400 line-clamp-3 mt-2">
                  "{src.snippet}"
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 space-y-2">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">Reliability Score:</span>
                  <span className="font-mono font-bold text-emerald-400">
                    {(src.reliability_score * 100).toFixed(0)}%
                  </span>
                </div>

                {src.reliability_rationale && (
                  <p className="text-[11px] text-slate-400 italic">
                    {src.reliability_rationale}
                  </p>
                )}

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] text-slate-400 font-mono">
                    {src.domain}
                  </span>
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
                  >
                    <span>Visit Source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 4: 11-SECTION RESEARCH DOSSIER */}
      {activeTab === 'report' && (
        <div className="space-y-6">
          <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-6 max-w-4xl mx-auto shadow-2xl">
            <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">{session.report?.report_title}</h2>
                <p className="text-xs text-slate-400 mt-1">Structured 11-Section Investigation Dossier</p>
              </div>
              <button
                onClick={handleCopyMarkdown}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-1.5"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>

            {/* Markdown rendered pre-block */}
            <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-sans bg-slate-950 p-6 rounded-xl border border-slate-800/80">
              {session.report?.markdown_content || "Report synthesis pending..."}
            </div>

            {/* Key Findings List */}
            {session.report?.key_findings && session.report.key_findings.length > 0 && (
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Key Findings Summary</h3>
                <ul className="space-y-2 text-xs text-slate-300">
                  {session.report.key_findings.map((f, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-indigo-400 font-bold">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
