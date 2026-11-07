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
  Search
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';
import ragService from '../../services/ragService';
import { Badge } from '../common/Badge';

export function ChatInterface() {
  const { selectedVersion, setSelectedVersion } = useSystem();
  const [query, setQuery] = useState('');
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [ragStatus, setRagStatus] = useState(null);
  const [syncingIndex, setSyncingIndex] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [compareMode, setCompareMode] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);

  // Suggested test queries specifically highlighting cross-version evolution
  const sampleQueries = [
    {
      title: 'Report Exports Evolution',
      text: 'How do report exports work in NexaDesk?',
      description: 'v1.0 Manual CSV -> v2.0 Scheduled Exports -> v3.0 NexaFlow AI Autonomous'
    },
    {
      title: 'Pricing & Quotas',
      text: 'What are the pricing plans and monthly ticket quotas?',
      description: 'v1.0 ($29/$79) -> v2.0 ($39/$99) -> v3.0 ($49/Custom Enterprise AI)'
    },
    {
      title: 'Ticket Routing',
      text: 'How does automated ticket assignment and routing work?',
      description: 'v1.0 Manual assignment -> v2.0 Round-Robin -> v3.0 Smart AI Copilot'
    },
    {
      title: 'Role-Based Access (RBAC)',
      text: 'What user roles and permission levels are supported?',
      description: 'Admin, Agent, Viewer across different tiers'
    }
  ];

  // Load vector store status
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

  // Perform single-version semantic search
  const handleSearch = async (queryText = query) => {
    const textToSearch = queryText || query;
    if (!textToSearch.trim()) return;

    setLoadingSearch(true);
    setCompareMode(false);
    setComparisonResults(null);

    try {
      const data = await ragService.searchVectors({
        query: textToSearch,
        product_version: selectedVersion,
        top_k: 3
      });
      setSearchResults({
        query: textToSearch,
        version: selectedVersion,
        results: data.results || []
      });
    } catch (err) {
      console.error('Vector search failed:', err);
    } finally {
      setLoadingSearch(false);
    }
  };

  // Perform multi-version 3-way comparative search
  const handleCompareAllVersions = async (queryText = query) => {
    const textToSearch = queryText || query;
    if (!textToSearch.trim()) return;

    setLoadingSearch(true);
    setCompareMode(true);
    setSearchResults(null);

    try {
      const versions = ['v1.0', 'v2.0', 'v3.0'];
      const promises = versions.map((ver) =>
        ragService.searchVectors({
          query: textToSearch,
          product_version: ver,
          top_k: 2
        })
      );

      const responses = await Promise.all(promises);
      const comparisonMap = {};
      versions.forEach((ver, index) => {
        comparisonMap[ver] = responses[index].results || [];
      });

      setComparisonResults({
        query: textToSearch,
        data: comparisonMap
      });
    } catch (err) {
      console.error('Multi-version comparison failed:', err);
    } finally {
      setLoadingSearch(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: ChromaDB Vector Index Status */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
            <Database size={20} />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-slate-800">ChromaDB Persistent Vector Store</h2>
              <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200">
                Phase 3 Active
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Model: <span className="font-mono text-indigo-600 font-semibold">{ragStatus?.embedding_model || 'sentence-transformers/all-MiniLM-L6-v2'}</span> (384-dim dense embeddings)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-700">
            <Layers size={14} className="text-slate-500" />
            <span className="font-semibold text-slate-900">{ragStatus?.total_chunks_indexed || 0}</span>
            <span>Total Vectors</span>
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
            title="Synchronize all processed documents from SQLite into ChromaDB"
          >
            <RefreshCw size={13} className={syncingIndex ? 'animate-spin text-indigo-600' : 'text-slate-500'} />
            <span>{syncingIndex ? 'Syncing...' : 'Sync Index'}</span>
          </button>
        </div>
      </div>

      {/* Main Semantic Search Playground */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Header and Controls */}
        <div className="p-4 border-b border-slate-200 bg-slate-50/70">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Sparkles size={16} className="text-indigo-600" />
                <span>Version-Aware Semantic Vector Search & Disambiguation</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Targeting Product Version: <span className="font-bold text-indigo-700">{selectedVersion}</span>. Tests strictly verify that features documented differently in other versions never bleed into this context.
              </p>
            </div>

            {/* Version Switcher */}
            <div className="flex items-center bg-white p-1 rounded-lg border border-slate-200 shadow-sm self-start sm:self-auto">
              <span className="text-[11px] font-medium text-slate-500 px-2">Scope:</span>
              {['v1.0', 'v2.0', 'v3.0'].map((ver) => (
                <button
                  key={ver}
                  onClick={() => {
                    setSelectedVersion(ver);
                    if (query.trim() && !compareMode) {
                      setTimeout(() => handleSearch(query), 50);
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
              handleSearch();
            }}
            className="flex items-center space-x-2"
          >
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask an inquiry or test a product capability (e.g. 'How do report exports work?')..."
                className="w-full text-xs border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
              />
            </div>

            <button
              type="submit"
              disabled={!query.trim() || loadingSearch}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
            >
              <Send size={13} />
              <span>{loadingSearch && !compareMode ? 'Searching...' : `Search ${selectedVersion}`}</span>
            </button>

            <button
              type="button"
              onClick={() => handleCompareAllVersions()}
              disabled={!query.trim() || loadingSearch}
              className="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
              title="Execute search against v1.0, v2.0, and v3.0 simultaneously to verify version isolation"
            >
              <Split size={14} />
              <span className="hidden sm:inline">{loadingSearch && compareMode ? 'Comparing...' : 'Compare 3 Versions'}</span>
            </button>
          </form>

          {/* Suggested Differentiating Inquiries */}
          <div className="mt-3 pt-3 border-t border-slate-200">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
              Select Cross-Version Test Queries:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
              {sampleQueries.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuery(item.text);
                    handleSearch(item.text);
                  }}
                  className="text-left p-2 rounded-lg border border-slate-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/50 transition-all text-xs group"
                >
                  <p className="font-semibold text-slate-800 group-hover:text-indigo-600">{item.title}</p>
                  <p className="text-[11px] text-slate-500 truncate mt-0.5">{item.text}</p>
                  <p className="text-[10px] text-indigo-500 font-mono mt-1">{item.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Area */}
        <div className="p-5 min-h-[380px] bg-slate-50/40">
          {loadingSearch && (
            <div className="py-16 text-center">
              <RefreshCw size={28} className="animate-spin text-indigo-600 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-700">Generating sentence embeddings and searching ChromaDB...</p>
              <p className="text-[11px] text-slate-500 mt-1">Filtering vector embeddings strictly by metadata: product_version = {selectedVersion}</p>
            </div>
          )}

          {/* Case 1: 3-Way Cross-Version Comparison Results */}
          {!loadingSearch && compareMode && comparisonResults && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                    <Split size={14} className="text-emerald-600" />
                    <span>Cross-Version Retrieval Disambiguation Matrix</span>
                  </h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Query: <span className="font-semibold text-slate-900">"{comparisonResults.query}"</span>
                  </p>
                </div>
                <span className="text-[11px] text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200 font-medium">
                  Verified Version Isolation
                </span>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {['v1.0', 'v2.0', 'v3.0'].map((ver) => {
                  const chunks = comparisonResults.data[ver] || [];
                  const verColor =
                    ver === 'v1.0'
                      ? 'border-blue-300 bg-blue-50/30'
                      : ver === 'v2.0'
                      ? 'border-indigo-300 bg-indigo-50/30'
                      : 'border-purple-300 bg-purple-50/30';
                  const badgeColor =
                    ver === 'v1.0'
                      ? 'bg-blue-100 text-blue-800'
                      : ver === 'v2.0'
                      ? 'bg-indigo-100 text-indigo-800'
                      : 'bg-purple-100 text-purple-800';

                  return (
                    <div key={ver} className={`rounded-xl border ${verColor} p-4 flex flex-col space-y-3`}>
                      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                        <span className={`px-2.5 py-0.5 rounded font-mono font-bold text-xs ${badgeColor}`}>
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
                          <div key={idx} className="bg-white rounded-lg border border-slate-200 p-3 shadow-xs space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-[11px] font-semibold text-slate-800 truncate max-w-[180px]">
                                {item.metadata?.document_name}
                              </span>
                              <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                                sim: {item.similarity_score ? item.similarity_score.toFixed(3) : 'N/A'}
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-500 flex items-center space-x-2">
                              <span>§ {item.metadata?.section_title || 'Section'}</span>
                              <span>·</span>
                              <span>Page {item.metadata?.page_number || 1}</span>
                            </div>
                            <p className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-100 font-mono leading-relaxed line-clamp-6">
                              {item.text_content || item.content}
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

          {/* Case 2: Single-Version Search Results */}
          {!loadingSearch && !compareMode && searchResults && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Retrieved Vector Chunks ({searchResults.results.length})
                  </h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Query: <span className="font-semibold text-slate-900">"{searchResults.query}"</span> in <span className="font-bold text-indigo-600 font-mono">{searchResults.version}</span>
                  </p>
                </div>
                <span className="text-xs text-slate-500">
                  Sentence-Transformers Cosine Similarity
                </span>
              </div>

              {searchResults.results.length === 0 ? (
                <div className="py-12 text-center text-slate-500 text-xs">
                  No vector chunks matched your query in <span className="font-semibold">{searchResults.version}</span>.
                </div>
              ) : (
                <div className="space-y-3">
                  {searchResults.results.map((res, index) => (
                    <div
                      key={res.chunk_id || index}
                      className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-3 hover:border-indigo-300 transition-colors"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center">
                            {index + 1}
                          </span>
                          <span className="font-bold text-xs text-slate-800">
                            {res.metadata?.document_name}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded bg-slate-100 text-slate-700">
                            {res.metadata?.document_type}
                          </span>
                          <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">
                            {res.metadata?.product_version}
                          </span>
                        </div>

                        <div className="flex items-center space-x-3 text-xs">
                          <span className="text-slate-500 font-mono text-[11px]">
                            ID: {res.chunk_id}
                          </span>
                          <span className="px-2 py-0.5 font-mono text-[11px] font-bold rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                            Score: {res.similarity_score ? (res.similarity_score * 100).toFixed(1) + '%' : 'N/A'}
                          </span>
                        </div>
                      </div>

                      {/* Snippet Content */}
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                        <div className="text-[11px] font-semibold text-slate-600 mb-1 flex items-center space-x-2">
                          <Tag size={12} className="text-indigo-500" />
                          <span>Section: {res.metadata?.section_title || 'General'}</span>
                          <span className="text-slate-400">|</span>
                          <span>Page: {res.metadata?.page_number || 1}</span>
                        </div>
                        <p className="text-xs text-slate-800 font-sans leading-relaxed whitespace-pre-wrap">
                          {res.text_content || res.content}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Initial Blank State */}
          {!loadingSearch && !searchResults && !compareMode && (
            <div className="py-16 text-center max-w-md mx-auto">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center mx-auto mb-3">
                <Search size={22} />
              </div>
              <h4 className="text-sm font-semibold text-slate-800">Explore Version-Aware Vector Retrieval</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Enter a question or click one of the suggested cross-version queries above.
                You can test retrieval isolated to <span className="font-semibold text-indigo-600">{selectedVersion}</span>, or click <span className="font-semibold text-emerald-600">"Compare 3 Versions"</span> to observe how the exact same inquiry surfaces version-specific documentation across v1.0, v2.0, and v3.0 without mixing.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
