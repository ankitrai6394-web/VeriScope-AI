import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, 
  Search, 
  Trash2, 
  ArrowRight, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Database,
  Calendar,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchSession } from '../types';
import { formatDate } from '../utils/format';

export const HistoryPage: React.FC = () => {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchFilter, setSearchFilter] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = () => {
    setLoading(true);
    api.getHistory(0, 100)
      .then(setSessions)
      .catch((err) => console.error("Error loading history:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this research session?")) return;

    setDeletingId(id);
    try {
      await api.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      console.error("Failed to delete session:", err);
    } finally {
      setDeletingId(null);
    }
  };

  const filteredSessions = sessions.filter((s) =>
    s.query.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center space-x-3">
            <History className="w-7 h-7 text-indigo-400" />
            <span>Research History</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Persisted research investigations, agent audit logs, and claim verifications.
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Search queries..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400 text-sm">
          Loading historical sessions...
        </div>
      ) : filteredSessions.length === 0 ? (
        <div className="text-center py-20 space-y-3 bg-slate-900/30 rounded-2xl border border-slate-800">
          <Database className="w-10 h-10 text-slate-400 mx-auto" />
          <h2 className="text-base font-bold text-white">No Research Sessions Found</h2>
          <p className="text-xs text-slate-400">
            {searchFilter ? "No sessions match your search filter." : "Start your first multi-agent investigation in the Workspace."}
          </p>
          <Link
            to="/workspace"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold mt-2"
          >
            <span>Go to Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSessions.map((session) => (
            <div
              key={session.id}
              className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex flex-wrap items-center gap-2 text-[11px]">
                  <span className="font-mono text-indigo-400 font-bold uppercase px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                    {session.mode} Mode
                  </span>
                  <span className="text-slate-400">
                    {formatDate(session.created_at)}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded-full font-bold ${
                      session.status === 'COMPLETED'
                        ? 'bg-emerald-950/80 text-emerald-400'
                        : session.status === 'FAILED'
                        ? 'bg-rose-950/80 text-rose-400'
                        : 'bg-indigo-950/80 text-indigo-400'
                    }`}
                  >
                    {session.status}
                  </span>
                </div>

                <Link
                  to={`/results/${session.id}`}
                  className="block text-base font-bold text-white hover:text-indigo-400 transition-colors"
                >
                  {session.query}
                </Link>

                <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-1">
                  <span>Sources: <strong className="text-slate-200">{session.total_sources}</strong></span>
                  <span>Claims: <strong className="text-slate-200">{session.total_claims}</strong></span>
                  <span>Supported: <strong className="text-emerald-400">{session.verified_claims}</strong></span>
                  <span>Contradicted: <strong className="text-rose-400">{session.contradicted_claims}</strong></span>
                </div>
              </div>

              <div className="flex items-center space-x-2 self-end sm:self-center">
                <Link
                  to={`/results/${session.id}`}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold flex items-center space-x-1 transition-all"
                >
                  <span>Dossier</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <button
                  type="button"
                  onClick={(e) => handleDelete(session.id, e)}
                  disabled={deletingId === session.id}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-rose-950 text-slate-400 hover:text-rose-400 border border-slate-700/60 transition-colors cursor-pointer"
                  aria-label="Delete Session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
