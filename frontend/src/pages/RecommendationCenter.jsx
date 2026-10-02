import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Lightbulb,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldAlert,
  BrainCircuit,
  Filter,
  Play,
  FileText,
  AlertTriangle,
  History,
  Sparkles
} from 'lucide-react';

export default function RecommendationCenter() {
  const { token, role } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [targetEntity, setTargetEntity] = useState('supplier:1');
  const [triggering, setTriggering] = useState(false);
  const [selectedRec, setSelectedRec] = useState(null);
  const [decisionNotes, setDecisionNotes] = useState('');
  const [modalMode, setModalMode] = useState(null); // 'approve' | 'reject' | null
  const [actionLoading, setActionLoading] = useState(false);
  const [memories, setMemories] = useState([]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const url = activeTab === 'all'
        ? '/api/v1/recommendations'
        : `/api/v1/recommendations?status=${activeTab}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMemories = async (entityId) => {
    try {
      const res = await fetch(`/api/v1/recommendations/memories/search?target_global_id=${entityId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMemories(data.memories || []);
      }
    } catch (err) {
      console.error('Failed to fetch memories:', err);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [activeTab, token]);

  const handleTriggerAgents = async () => {
    if (!targetEntity.trim()) return;
    setTriggering(true);
    try {
      const res = await fetch('/api/v1/agents/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ target_global_id: targetEntity })
      });
      if (res.ok) {
        await fetchRecommendations();
        await fetchMemories(targetEntity);
      }
    } catch (err) {
      console.error('Trigger agent error:', err);
    } finally {
      setTriggering(false);
    }
  };

  const handleDecision = async () => {
    if (!selectedRec || !modalMode) return;
    setActionLoading(true);
    try {
      const url = `/api/v1/recommendations/${selectedRec.recommendation_id}/${modalMode}`;
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ notes: decisionNotes })
      });

      if (res.ok) {
        setModalMode(null);
        setSelectedRec(null);
        setDecisionNotes('');
        await fetchRecommendations();
      } else {
        const err = await res.json();
        alert(`Decision error: ${err.detail || 'Failed to submit decision'}`);
      }
    } catch (err) {
      console.error('Submit decision failed:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const parseCitations = (citationsJson) => {
    if (!citationsJson) return [];
    try {
      return JSON.parse(citationsJson);
    } catch (e) {
      return [];
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <Lightbulb className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                Recommendation Approval Center
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Human-in-the-Loop
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Multi-agent candidate proposals with persistent disruption memory citations & human governance.
              </p>
            </div>
          </div>
        </div>

        {/* Trigger Multi-Agent Pipeline Widget */}
        <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded-xl border border-slate-800">
          <input
            type="text"
            value={targetEntity}
            onChange={(e) => setTargetEntity(e.target.value)}
            placeholder="e.g. supplier:1"
            className="bg-slate-900 text-slate-200 text-xs px-3 py-2 rounded-lg border border-slate-800 focus:outline-none focus:border-indigo-500 w-36 font-mono"
          />
          <button
            onClick={handleTriggerAgents}
            disabled={triggering}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium px-3.5 py-2 rounded-lg transition-colors shadow-lg shadow-indigo-600/20"
          >
            {triggering ? (
              <BrainCircuit className="w-4 h-4 animate-spin text-indigo-200" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>{triggering ? 'Reasoning...' : 'Trigger Pipeline'}</span>
          </button>
        </div>
      </div>

      {/* Human Governance Governance Banner */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-start space-x-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <strong className="text-amber-300 font-semibold">Strict Governance Safety Enforcement (SRS §4.5 & NFR-S1):</strong>
          Recommendation proposals generated by the multi-agent layer default strictly to status <code className="bg-amber-950/50 px-1 py-0.5 rounded text-amber-300">pending</code>.
          Decisions are never auto-applied regardless of risk score or LLM confidence. Every Accept or Reject action requires explicit Supply Chain Manager authentication and logs an indelible audit entry.
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          {[
            { id: 'pending', label: 'Pending Approval', icon: Clock, color: 'text-amber-400' },
            { id: 'accepted', label: 'Approved / Accepted', icon: CheckCircle2, color: 'text-emerald-400' },
            { id: 'rejected', label: 'Rejected', icon: XCircle, color: 'text-rose-400' },
            { id: 'all', label: 'All Recommendations', icon: Filter, color: 'text-slate-400' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-slate-800 text-slate-100 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <tab.icon className={`w-4 h-4 ${tab.color}`} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="text-xs text-slate-500 font-mono">
          Showing {recommendations.length} records
        </div>
      </div>

      {/* Recommendation Cards Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
          <BrainCircuit className="w-5 h-5 animate-spin text-indigo-400 mr-2" />
          Loading recommendation records...
        </div>
      ) : recommendations.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center">
          <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-300 font-medium text-sm">No {activeTab} recommendations found</p>
          <p className="text-slate-500 text-xs mt-1">
            Trigger the multi-agent pipeline above or disrupt an entity to generate new candidate mitigation proposals.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {recommendations.map((rec) => {
            const citations = parseCitations(rec.memory_citations_json);
            return (
              <div
                key={rec.recommendation_id}
                className={`bg-slate-900/70 border rounded-2xl p-5 backdrop-blur-sm transition-all hover:border-slate-700 ${
                  rec.status === 'pending'
                    ? 'border-amber-500/30 bg-amber-500/[0.02]'
                    : rec.status === 'accepted'
                    ? 'border-emerald-500/30 bg-emerald-500/[0.02]'
                    : 'border-slate-800 bg-slate-900/40 opacity-80'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                      {/* Status Tag */}
                      <span
                        className={`text-[11px] font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider flex items-center space-x-1 ${
                          rec.status === 'pending'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : rec.status === 'accepted'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {rec.status === 'pending' && <Clock className="w-3 h-3 mr-1" />}
                        {rec.status === 'accepted' && <CheckCircle2 className="w-3 h-3 mr-1" />}
                        {rec.status === 'rejected' && <XCircle className="w-3 h-3 mr-1" />}
                        {rec.status}
                      </span>

                      {/* Action Type */}
                      <span className="text-[11px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-full">
                        {rec.action_type}
                      </span>

                      {/* Confidence Score */}
                      <span className="text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md">
                        {Math.round(rec.confidence_score * 100)}% Confidence
                      </span>

                      {/* Target Entity */}
                      <span className="text-[11px] font-mono text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                        Target: {rec.entity_global_id}
                      </span>
                    </div>

                    <h3 className="text-base font-semibold text-slate-100">{rec.title}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>

                    {/* Disruption Memory Citations (Configuration C Evidence) */}
                    {citations.length > 0 && (
                      <div className="mt-3 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 space-y-2">
                        <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400">
                          <History className="w-4 h-4 text-indigo-400" />
                          <span>Retrieved Disruption Memory Citations (Configuration C)</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                          {citations.map((mem, i) => (
                            <div key={i} className="bg-slate-900 p-2 rounded-lg border border-slate-800/80">
                              <div className="text-slate-200 font-medium">{mem.action_taken}</div>
                              <div className="text-slate-400 text-[10px] mt-0.5">
                                Outcome Score: <strong className="text-emerald-400">{mem.outcome_score}%</strong> • Root Cause: {mem.root_cause}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Decision Actions */}
                  {rec.status === 'pending' && (
                    <div className="flex items-center space-x-2 shrink-0 md:self-center">
                      <button
                        onClick={() => {
                          setSelectedRec(rec);
                          setModalMode('approve');
                        }}
                        className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg shadow-emerald-600/20"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Accept & Execute</span>
                      </button>
                      <button
                        onClick={() => {
                          setSelectedRec(rec);
                          setModalMode('reject');
                        }}
                        className="flex items-center space-x-1.5 bg-slate-800 hover:bg-rose-600/20 hover:text-rose-400 text-slate-300 border border-slate-700 text-xs font-medium px-3.5 py-2.5 rounded-xl transition-all"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Reject</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Decision Modal */}
      {modalMode && selectedRec && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                {modalMode === 'approve' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-400" />
                )}
                <h3 className="text-base font-bold text-slate-100">
                  {modalMode === 'approve' ? 'Approve Mitigation Action' : 'Reject Recommendation'}
                </h3>
              </div>
              <button
                onClick={() => setModalMode(null)}
                className="text-slate-500 hover:text-slate-300 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <div className="text-xs text-slate-300 space-y-2">
              <div>
                <strong className="text-slate-400">Target Entity:</strong>{' '}
                <code className="text-indigo-400 bg-slate-950 px-1 py-0.5 rounded">{selectedRec.entity_global_id}</code>
              </div>
              <div>
                <strong className="text-slate-400">Action:</strong> {selectedRec.title}
              </div>
              <p className="text-slate-400 italic bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-[11px]">
                "{selectedRec.description}"
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">
                Supply Chain Manager Rationale / Notes:
              </label>
              <textarea
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                placeholder={
                  modalMode === 'approve'
                    ? 'Enter approval rationale (e.g. Alternate supplier capacity verified with 95% on-time performance).'
                    : 'Enter rejection rationale (e.g. Transit rerouting cost exceeds operational budget threshold).'
                }
                rows={3}
                className="w-full bg-slate-950 text-slate-200 text-xs p-3 rounded-xl border border-slate-800 focus:outline-none focus:border-indigo-500 resize-none"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setModalMode(null)}
                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={handleDecision}
                disabled={actionLoading}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold text-white transition-all shadow-lg ${
                  modalMode === 'approve'
                    ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20'
                    : 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/20'
                }`}
              >
                {actionLoading && <BrainCircuit className="w-4 h-4 animate-spin" />}
                <span>
                  {actionLoading
                    ? 'Recording...'
                    : modalMode === 'approve'
                    ? 'Confirm Approval'
                    : 'Confirm Rejection'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
