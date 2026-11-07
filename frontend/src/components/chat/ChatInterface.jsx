import React, { useState, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  Layers,
  Database,
  RefreshCw,
  HelpCircle,
  FileText,
  Tag,
  CheckCircle2,
  ArrowRight,
  Split,
  Search,
  Sliders,
  Terminal,
  Activity,
  Zap,
  Info
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';
import ragService from '../../services/ragService';
import { Badge } from '../common/Badge';

export function ChatInterface() {
  const { selectedVersion, setSelectedVersion } = useSystem();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [ragStatus, setRagStatus] = useState(null);
  const [syncingIndex, setSyncingIndex] = useState(false);

  // Retrieval Settings
  const [retrievalMode, setRetrievalMode] = useState('hybrid'); // 'hybrid', 'dense_only', 'sparse_only'
  const [enableRewriting, setEnableRewriting] = useState(true);
  const [topK, setTopK] = useState(4);
  const [denseWeight, setDenseWeight] = useState(0.6);
  const [sparseWeight, setSparseWeight] = useState(0.4);

  // Results State
  const [retrievalData, setRetrievalData] = useState(null);
  const [activeView, setActiveView] = useState('results'); // 'results', 'compare_methods', 'compare_versions'
  const [methodsComparison, setMethodsComparison] = useState(null);
  const [versionComparison, setVersionComparison] = useState(null);

  // Suggested informal customer questions specifically illustrating Phase 4 rewriting & hybrid retrieval
  const sampleQuestions = [
    {
      title: "Why can't I schedule my reports like before?",
      category: 'Reporting & Exports',
      description: 'Tests informal complaint -> transforms to "Scheduled report export configuration"'
    },
    {
      title: 'How much do I have to pay per user and can I get a discount for paying for a whole year?',
      category: 'Pricing & Quotas',
      description: 'Tests colloquial billing question -> transforms to "Subscription pricing plans annual discount"'
    },
    {
      title: 'Can someone tell me how round robin ticket assignment works?',
      category: 'Ticket Routing',
      description: 'Tests conversational query -> transforms to "Automated ticket routing round robin rules"'
    },
    {
      title: 'What are the admin role permissions and how do I add agents?',
      category: 'User Roles & RBAC',
      description: 'Tests conversational permission enquiry -> transforms to "Role-based access control user management"'
    }
  ];

  // Fetch status of ChromaDB and BM25 index
  const fetchRagStatus = async () => {
    try {
      const data = await ragService.getStatus();
      setRagStatus(data);
    } catch (err) {
      console.error('Failed to fetch RAG status:', err);
    }
  };

  useEffect(() => {
    fetchRagStatus();
  }, []);

  // Handle re-indexing
  const handleReindex = async () => {
    setSyncingIndex(true);
    try {
      await ragService.reindexAll();
      await fetchRagStatus();
    } catch (err) {
      console.error('Re-indexing failed:', err);
    } finally {
      setSyncingIndex(false);
    }
  };

  // Execute full Phase 4 Hybrid Retrieval Pipeline
  const handleRetrieve = async (textToSearch = query) => {
    const q = textToSearch || query;
    if (!q.trim()) return;

    setLoading(true);
    setActiveView('results');
    setMethodsComparison(null);
    setVersionComparison(null);

    try {
      const res = await ragService.retrieveHybrid({
        customer_question: q,
        product_version: selectedVersion,
        product_name: 'NexaDesk',
        enable_query_rewriting: enableRewriting,
        retrieval_mode: retrievalMode,
        top_k: topK,
        dense_weight: denseWeight,
        sparse_weight: sparseWeight,
        similarity_threshold: 0.0
      });
      setRetrievalData(res);
    } catch (err) {
      console.error('Hybrid retrieval failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Execute 3-Way Retrieval Method Comparison (Phase 4 Part E)
  const handleCompareMethods = async (textToSearch = query) => {
    const q = textToSearch || query;
    if (!q.trim()) return;

    setLoading(true);
    setActiveView('compare_methods');
    setRetrievalData(null);
    setVersionComparison(null);

    try {
      const res = await ragService.compareRetrievalMethods({
        customer_question: q,
        product_version: selectedVersion,
        product_name: 'NexaDesk',
        top_k: 3
      });
      setMethodsComparison(res);
    } catch (err) {
      console.error('Method comparison failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Execute 3-Way Cross-Version Comparison (Phase 3 + 4 version isolation)
  const handleCompareVersions = async (textToSearch = query) => {
    const q = textToSearch || query;
    if (!q.trim()) return;

    setLoading(true);
    setActiveView('compare_versions');
    setRetrievalData(null);
    setMethodsComparison(null);

    try {
      const versions = ['v1.0', 'v2.0', 'v3.0'];
      const promises = versions.map((ver) =>
        ragService.retrieveHybrid({
          customer_question: q,
          product_version: ver,
          enable_query_rewriting: enableRewriting,
          retrieval_mode: retrievalMode,
          top_k: 2
        })
      );
      const responses = await Promise.all(promises);
      const comparisonMap = {};
      versions.forEach((ver, idx) => {
        comparisonMap[ver] = responses[idx];
      });

      setVersionComparison({
        query: q,
        versions: comparisonMap
      });
    } catch (err) {
      console.error('Cross-version comparison failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Hybrid Engine Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
            <Zap size={20} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-slate-800">Version-Aware Hybrid Retrieval Pipeline</h2>
              <span className="px-2 py-0.5 text-[11px] font-semibold bg-indigo-100 text-indigo-800 rounded-full border border-indigo-200">
                Phase 4 Active
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Dense: <span className="font-mono text-indigo-600 font-semibold">{ragStatus?.embedding_model || 'sentence-transformers/all-MiniLM-L6-v2'}</span> ·
              Sparse: <span className="font-mono text-emerald-600 font-semibold">{ragStatus?.sparse_model || 'BM25Okapi'}</span> ·
              Fusion: <span className="font-mono text-slate-700 font-semibold">Reciprocal Rank Fusion (RRF k=60)</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-700">
            <Layers size={14} className="text-slate-500" />
            <span className="font-semibold text-slate-900">{ragStatus?.total_chunks_indexed || 0}</span>
            <span>Vectors</span>
            <span className="text-slate-300">|</span>
            <span className="font-mono text-[11px]">
              v1.0: <span className="font-bold text-indigo-600">{ragStatus?.by_version?.['v1.0'] || 0}</span> ·
              v2.0: <span className="font-bold text-indigo-600">{ragStatus?.by_version?.['v2.0'] || 0}</span> ·
              v3.0: <span className="font-bold text-indigo-600">{ragStatus?.by_version?.['v3.0'] || 0}</span>
            </span>
          </div>

          <button
            onClick={handleReindex}
            disabled={syncingIndex}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg transition-colors shadow-sm disabled:opacity-50"
            title="Synchronize ChromaDB and reset BM25 cache"
          >
            <RefreshCw size={13} className={syncingIndex ? 'animate-spin text-indigo-600' : 'text-slate-500'} />
            <span>{syncingIndex ? 'Syncing...' : 'Sync Index'}</span>
          </button>
        </div>
      </div>

      {/* Main Retrieval Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Controls Bar */}
        <div className="p-4 border-b border-slate-200 bg-slate-50/70 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Sparkles size={16} className="text-indigo-600" />
                <span>Customer Inquiry & Hybrid Retrieval Console</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Target Product Scope: <span className="font-bold text-indigo-700 font-mono">{selectedVersion}</span>. Evaluates informal queries, query rewriting, and hybrid rank fusion.
              </p>
            </div>

            {/* Scope Version Selector */}
            <div className="flex items-center bg-white p-1 rounded-lg border border-slate-200 shadow-sm self-start sm:self-auto">
              <span className="text-[11px] font-medium text-slate-500 px-2">Scope:</span>
              {['v1.0', 'v2.0', 'v3.0'].map((ver) => (
                <button
                  key={ver}
                  onClick={() => {
                    setSelectedVersion(ver);
                    if (query.trim() && activeView === 'results') {
                      setTimeout(() => handleRetrieve(query), 50);
                    }
                  }}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                    selectedVersion === ver
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {ver}
                </button>
              ))}
            </div>
          </div>

          {/* Search Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleRetrieve();
            }}
            className="flex items-center space-x-2"
          >
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask an informal customer question (e.g. 'Why can\'t I schedule my reports like before?')..."
                className="w-full text-xs border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white shadow-xs"
              />
            </div>

            <button
              type="submit"
              disabled={!query.trim() || loading}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
            >
              <Send size={13} />
              <span>{loading && activeView === 'results' ? 'Retrieving...' : `Retrieve (${selectedVersion})`}</span>
            </button>

            <button
              type="button"
              onClick={() => handleCompareMethods()}
              disabled={!query.trim() || loading}
              className="px-3.5 py-2.5 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
              title="Compare Raw Dense vs Rewritten Dense vs Rewritten Hybrid (Phase 4 Part E)"
            >
              <Sliders size={13} />
              <span className="hidden md:inline">Compare 3 Methods</span>
            </button>

            <button
              type="button"
              onClick={() => handleCompareVersions()}
              disabled={!query.trim() || loading}
              className="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
              title="Compare retrieval across v1.0, v2.0, and v3.0 simultaneously"
            >
              <Split size={14} />
              <span className="hidden md:inline">Compare Versions</span>
            </button>
          </form>

          {/* Config Strip */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-slate-600 border-t border-slate-200">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1.5">
                <span className="font-medium text-slate-500">Mode:</span>
                <select
                  value={retrievalMode}
                  onChange={(e) => setRetrievalMode(e.target.value)}
                  className="bg-white border border-slate-300 rounded px-2 py-0.5 text-xs font-semibold text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="hybrid">Hybrid (Dense + BM25 RRF)</option>
                  <option value="dense_only">Dense Vector Only</option>
                  <option value="sparse_only">Sparse BM25 Only</option>
                </select>
              </div>

              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableRewriting}
                  onChange={(e) => setEnableRewriting(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-slate-700 font-medium">Query Rewriting (Gemini / Heuristic)</span>
              </label>
            </div>

            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-500">
              <span>Weights: Dense({denseWeight}) + Sparse({sparseWeight})</span>
              <span>·</span>
              <span>Top K: {topK}</span>
            </div>
          </div>

          {/* Suggested Informal Questions */}
          <div className="pt-2">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Select Sample Informal Inquiries:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
              {sampleQuestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuery(item.title);
                    handleRetrieve(item.title);
                  }}
                  className="text-left p-2 rounded-lg border border-slate-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/50 transition-all text-xs group"
                >
                  <span className="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider block">
                    {item.category}
                  </span>
                  <p className="font-semibold text-slate-800 group-hover:text-indigo-600 truncate mt-0.5">
                    {item.title}
                  </p>
                  <p className="text-[10px] text-slate-500 truncate mt-1">
                    {item.description}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="p-5 min-h-[400px] bg-slate-50/40">
          {loading && (
            <div className="py-20 text-center">
              <RefreshCw size={30} className="animate-spin text-indigo-600 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-800">Processing Pipeline...</p>
              <p className="text-[11px] text-slate-500 mt-1">
                Query Rewriting → Version Filtering ({selectedVersion}) → Dense & BM25 Scoring → Reciprocal Rank Fusion
              </p>
            </div>
          )}

          {/* VIEW 1: Standard Hybrid Retrieval Results + Query Rewriting Card */}
          {!loading && activeView === 'results' && retrievalData && (
            <div className="space-y-4">
              {/* Part A & E: Query Rewriting Card */}
              {retrievalData.rewritten_query && (
                <div className="bg-indigo-50/70 border border-indigo-200 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between pb-1 border-b border-indigo-100">
                    <div className="flex items-center space-x-2">
                      <Terminal size={14} className="text-indigo-600" />
                      <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                        Query Rewriting Module (Phase 4 Part A)
                      </span>
                    </div>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-indigo-200/60 text-indigo-800 font-semibold">
                      Rewriter: {retrievalData.diagnostics?.rewriter_used || 'heuristic_fallback'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 block">Original Informal Question:</span>
                      <p className="text-slate-800 italic mt-0.5">"{retrievalData.original_query}"</p>
                    </div>
                    <div>
                      <span className="text-[11px] font-semibold text-indigo-600 block">Documentation Search Query:</span>
                      <p className="text-indigo-950 font-semibold mt-0.5 font-mono">
                        "{retrievalData.rewritten_query}"
                      </p>
                    </div>
                  </div>

                  {retrievalData.search_keywords?.length > 0 && (
                    <div className="flex items-center space-x-1.5 pt-1">
                      <span className="text-[10px] font-semibold text-slate-500">Keywords:</span>
                      <div className="flex flex-wrap gap-1">
                        {retrievalData.search_keywords.map((kw, i) => (
                          <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-white text-indigo-700 border border-indigo-200 font-mono">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Status Header */}
              <div className="flex items-center justify-between pb-1 border-b border-slate-200">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
                    <Activity size={14} className="text-emerald-600" />
                    <span>Retrieved Documentation Chunks ({retrievalData.results.length})</span>
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Mode: <span className="font-semibold text-slate-700 capitalize">{retrievalData.retrieval_mode}</span> · Latency: <span className="font-mono text-indigo-600">{retrievalData.diagnostics?.latency_ms} ms</span>
                  </p>
                </div>
                <span className="text-xs px-2.5 py-1 rounded bg-slate-100 text-slate-700 font-mono font-semibold">
                  Scope: {retrievalData.product_version}
                </span>
              </div>

              {retrievalData.results.length === 0 ? (
                <div className="py-12 text-center text-slate-500 text-xs">
                  {retrievalData.status_message}
                </div>
              ) : (
                <div className="space-y-3">
                  {retrievalData.results.map((item, index) => (
                    <div
                      key={item.chunk_id || index}
                      className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-2.5 hover:border-indigo-300 transition-colors"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center">
                            {item.rank}
                          </span>
                          <span className="font-bold text-xs text-slate-800">
                            {item.document_name}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded bg-slate-100 text-slate-700">
                            {item.document_type}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">
                            {item.product_version}
                          </span>
                        </div>

                        <div className="flex items-center space-x-2 text-xs">
                          {item.dense_score !== null && (
                            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                              Dense: {item.dense_score.toFixed(3)}
                            </span>
                          )}
                          {item.sparse_score !== null && (
                            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                              BM25: {item.sparse_score.toFixed(3)}
                            </span>
                          )}
                          <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 border border-indigo-300">
                            RRF: {(item.rrf_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {/* Snippet */}
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                        <div className="text-[11px] font-semibold text-slate-600 mb-1 flex items-center space-x-2">
                          <Tag size={12} className="text-indigo-500" />
                          <span>Section: {item.section_title || 'General'}</span>
                          <span className="text-slate-400">|</span>
                          <span>Page {item.page_number || 1}</span>
                          <span className="text-slate-400">|</span>
                          <span className="font-mono text-[10px] text-slate-400">ID: {item.chunk_id}</span>
                        </div>
                        <p className="text-xs text-slate-800 font-sans leading-relaxed whitespace-pre-wrap">
                          {item.text_content}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* VIEW 2: 3-Way Retrieval Method Comparison (Phase 4 Part E) */}
          {!loading && activeView === 'compare_methods' && methodsComparison && (
            <div className="space-y-4">
              <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4">
                <div className="flex items-center justify-between pb-2 border-b border-amber-200">
                  <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center space-x-2">
                    <Sliders size={14} className="text-amber-700" />
                    <span>3-Way Retrieval Strategy Comparison Matrix (Phase 4 Part E)</span>
                  </h4>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold">
                    Target: {methodsComparison.product_version}
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-2">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-500">Raw Question:</span>
                    <p className="text-slate-800 italic font-medium">"{methodsComparison.original_query}"</p>
                  </div>
                  <div>
                    <span className="text-[11px] font-semibold text-amber-800">Rewritten Query:</span>
                    <p className="text-amber-950 font-bold font-mono">"{methodsComparison.rewritten_query}"</p>
                  </div>
                </div>
              </div>

              {/* 3 Columns */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Method 1: Raw Dense */}
                <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-3">
                  <div className="pb-2 border-b border-slate-200">
                    <span className="text-xs font-bold text-slate-800 uppercase block">1. Raw Query + Dense</span>
                    <span className="text-[10px] text-slate-500">ChromaDB semantic search with informal customer text</span>
                  </div>
                  {methodsComparison.raw_dense_results?.map((r, i) => (
                    <div key={i} className="bg-slate-50 rounded-lg p-2.5 border border-slate-200 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 truncate max-w-[150px]">{r.document_name}</span>
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                          sim: {r.dense_score?.toFixed(3)}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 font-medium">§ {r.section_title}</p>
                      <p className="text-[11px] text-slate-700 font-mono line-clamp-4 bg-white p-2 rounded border border-slate-100">
                        {r.text_content}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Method 2: Rewritten Dense */}
                <div className="bg-white rounded-xl border border-blue-200 p-4 space-y-3">
                  <div className="pb-2 border-b border-blue-100">
                    <span className="text-xs font-bold text-blue-900 uppercase block">2. Rewritten + Dense</span>
                    <span className="text-[10px] text-blue-600">Dense search using technical rewritten documentation terms</span>
                  </div>
                  {methodsComparison.rewritten_dense_results?.map((r, i) => (
                    <div key={i} className="bg-blue-50/40 rounded-lg p-2.5 border border-blue-200 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 truncate max-w-[150px]">{r.document_name}</span>
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                          sim: {r.dense_score?.toFixed(3)}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 font-medium">§ {r.section_title}</p>
                      <p className="text-[11px] text-slate-700 font-mono line-clamp-4 bg-white p-2 rounded border border-blue-100">
                        {r.text_content}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Method 3: Rewritten Hybrid */}
                <div className="bg-white rounded-xl border border-indigo-300 p-4 space-y-3 ring-1 ring-indigo-200">
                  <div className="pb-2 border-b border-indigo-100">
                    <span className="text-xs font-bold text-indigo-900 uppercase block">3. Rewritten + Hybrid (RRF)</span>
                    <span className="text-[10px] text-indigo-600">Rewritten technical query fused via Dense + BM25</span>
                  </div>
                  {methodsComparison.rewritten_hybrid_results?.map((r, i) => (
                    <div key={i} className="bg-indigo-50/40 rounded-lg p-2.5 border border-indigo-200 space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 truncate max-w-[150px]">{r.document_name}</span>
                        <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                          RRF: {(r.rrf_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 font-medium">§ {r.section_title}</p>
                      <p className="text-[11px] text-slate-700 font-mono line-clamp-4 bg-white p-2 rounded border border-indigo-100">
                        {r.text_content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 3: Cross-Version Comparison (v1.0 vs v2.0 vs v3.0) */}
          {!loading && activeView === 'compare_versions' && versionComparison && (
            <div className="space-y-4">
              <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4">
                <div className="flex items-center justify-between pb-2 border-b border-emerald-200">
                  <h4 className="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center space-x-2">
                    <Split size={14} className="text-emerald-700" />
                    <span>Cross-Version Disambiguation Matrix (Strict Multi-Version Isolation)</span>
                  </h4>
                  <span className="text-[11px] text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded font-medium">
                    Verified Zero Cross-Contamination
                  </span>
                </div>
                <p className="text-xs text-slate-700 mt-2">
                  Inquiry: <span className="font-semibold text-slate-900 font-mono">"{versionComparison.query}"</span>
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {['v1.0', 'v2.0', 'v3.0'].map((ver) => {
                  const data = versionComparison.versions[ver];
                  const chunks = data?.results || [];

                  return (
                    <div key={ver} className="bg-white rounded-xl border border-slate-200 p-4 space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                        <span className="px-2.5 py-0.5 rounded font-mono font-bold text-xs bg-indigo-100 text-indigo-800">
                          {ver}
                        </span>
                        <span className="text-[11px] text-slate-500 font-medium">
                          {chunks.length} Top Chunks
                        </span>
                      </div>

                      {chunks.length === 0 ? (
                        <p className="text-xs text-slate-400 italic py-6 text-center">No matching vectors found.</p>
                      ) : (
                        chunks.map((item, idx) => (
                          <div key={idx} className="bg-slate-50 rounded-lg border border-slate-200 p-3 space-y-1.5 text-xs">
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-800 truncate max-w-[170px]">
                                {item.document_name}
                              </span>
                              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700">
                                RRF: {(item.rrf_score * 100).toFixed(0)}%
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-500">§ {item.section_title}</div>
                            <p className="text-xs text-slate-700 bg-white p-2.5 rounded border border-slate-100 font-mono leading-relaxed line-clamp-5">
                              {item.text_content}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Initial Blank State */}
          {!loading && !retrievalData && !methodsComparison && !versionComparison && (
            <div className="py-20 text-center max-w-md mx-auto">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center mx-auto mb-3">
                <Search size={22} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800">Explore Version-Aware Hybrid Retrieval</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Type an informal customer question or click one of the suggested inquiries above.
                You can test single-version hybrid retrieval, click <span className="font-semibold text-amber-600">"Compare 3 Methods"</span> to benchmark Raw vs Rewritten vs Hybrid, or click <span className="font-semibold text-emerald-600">"Compare Versions"</span> to inspect cross-version isolation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
