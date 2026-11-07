import React, { useState, useEffect } from 'react';
import {
  FileText,
  Database,
  Layers,
  Activity,
  Bot,
  Clock,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  MessageSquare,
  Cpu,
  Server,
  Zap,
  ArrowRight,
  TrendingUp,
  ShieldCheck
} from 'lucide-react';
import { useSystem } from '../context/SystemContext';
import documentService from '../services/documentService';
import ragService from '../services/ragService';
import chatService from '../services/chatService';
import analyticsService from '../services/analyticsService';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Alert } from '../components/common/Alert';

export function DashboardPage() {
  const { health, systemInfo, loading: healthLoading, refreshHealth, selectedVersion, setSelectedVersion } = useSystem();

  const [stats, setStats] = useState(null);
  const [ragStatus, setRagStatus] = useState(null);
  const [recentDocs, setRecentDocs] = useState([]);
  const [recentEnquiries, setRecentEnquiries] = useState([]);
  const [analyticsOverview, setAnalyticsOverview] = useState(null);
  const [chatConfig, setChatConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, ragData, docsData, logsData, analyticsData, configData] = await Promise.allSettled([
        documentService.getStats(),
        ragService.getStatus(),
        documentService.listDocuments({ limit: 6 }),
        chatService.getRecentLogs(6),
        analyticsService.getOverview(),
        chatService.getConfig(),
      ]);

      if (statsData.status === 'fulfilled') setStats(statsData.value);
      if (ragData.status === 'fulfilled') setRagStatus(ragData.value);
      if (docsData.status === 'fulfilled') setRecentDocs(docsData.value.documents || []);
      if (logsData.status === 'fulfilled') setRecentEnquiries(logsData.value.history || []);
      if (analyticsData.status === 'fulfilled') setAnalyticsOverview(analyticsData.value);
      if (configData.status === 'fulfilled') setChatConfig(configData.value);
    } catch (err) {
      console.error('Failed to load admin dashboard data:', err);
      setError(err.message || 'Error fetching dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const totalDocs = stats?.total_documents ?? health?.stats?.total_documents ?? 0;
  const totalChunks = stats?.total_chunks ?? ragStatus?.total_chunks_indexed ?? 0;
  const activeProducts = ['NexaDesk'];
  const activeVersions = systemInfo?.supported_product_versions || ['v1.0', 'v2.0', 'v3.0'];
  const totalQueries = analyticsOverview?.total_queries ?? recentEnquiries.length ?? 0;
  const avgLatency = analyticsOverview?.avg_latency_ms ?? 0;

  const activeProvider = chatConfig?.active_provider || 'gemini';
  const activeModel = chatConfig?.llm_model || 'gemini-1.5-flash';

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Admin System Dashboard</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Project 32
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Real-time monitoring across Document Ingestion, ChromaDB Vector Indexing, Hybrid Retrieval, and LLM Generation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs">
            <Server size={14} className="text-slate-500" />
            <span className="text-slate-600 font-medium">Provider:</span>
            <span className="font-bold text-slate-900 uppercase">{activeProvider}</span>
            <span className="text-slate-400">({activeModel})</span>
          </div>

          <button
            onClick={() => { refreshHealth(); loadDashboardData(); }}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors shadow-xs"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin text-indigo-600' : ''} />
            <span>Refresh Metrics</span>
          </button>
        </div>
      </div>

      {error && (
        <Alert
          type="error"
          title="Metric Synchronization Notice"
          message={error}
          onRetry={loadDashboardData}
        />
      )}

      {/* 5 Real KPI Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        {/* Total Documents */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Total Documents</span>
            <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
              <FileText size={16} />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{totalDocs}</div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center space-x-1">
            <CheckCircle2 size={12} className="text-emerald-500" />
            <span>Ingested & Validated</span>
          </div>
        </div>

        {/* Total Indexed Chunks */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Vector Embeddings</span>
            <div className="p-1.5 rounded-lg bg-purple-50 text-purple-600">
              <Layers size={16} />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{totalChunks}</div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center space-x-1">
            <Database size={12} className="text-purple-500" />
            <span>ChromaDB Persistent</span>
          </div>
        </div>

        {/* Available Products */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Supported Product</span>
            <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
              <ShieldCheck size={16} />
            </div>
          </div>
          <div className="text-xl font-bold text-slate-900 truncate">NexaDesk</div>
          <div className="text-[11px] text-slate-500 mt-1">Multi-Version SaaS</div>
        </div>

        {/* Product Versions */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Active Versions</span>
            <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
              <Cpu size={16} />
            </div>
          </div>
          <div className="flex items-center space-x-1 text-sm font-bold text-slate-900 mt-1">
            {activeVersions.map((v) => (
              <span key={v} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-xs">
                {v}
              </span>
            ))}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Isolated Boundaries</div>
        </div>

        {/* Queries Served */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs col-span-2 md:col-span-1">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Customer Enquiries</span>
            <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <MessageSquare size={16} />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">{totalQueries}</div>
          <div className="text-[11px] text-slate-500 mt-1 flex items-center space-x-1">
            <TrendingUp size={12} className="text-blue-500" />
            <span>Avg {avgLatency > 0 ? `${avgLatency} ms` : 'Sub-second'}</span>
          </div>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 cols): Documents & Processing Status */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Document Uploads Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText size={17} className="text-indigo-600" />
                <h3 className="font-bold text-sm text-slate-900">Recent Document Ingestions</h3>
              </div>
              <span className="text-xs text-slate-500 font-mono">
                {recentDocs.length} shown of {totalDocs}
              </span>
            </div>

            {recentDocs.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No documents uploaded yet. Go to Document Catalog to upload initial product docs.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-4 font-semibold">Document Name</th>
                      <th className="py-2.5 px-3 font-semibold">Version</th>
                      <th className="py-2.5 px-3 font-semibold">Category</th>
                      <th className="py-2.5 px-3 font-semibold">Chunks</th>
                      <th className="py-2.5 px-3 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recentDocs.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="py-2.5 px-4 font-medium text-slate-800 flex items-center space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                          <span className="truncate max-w-[220px]" title={doc.document_name}>
                            {doc.document_name}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700">
                            {doc.product_version}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-600">{doc.category}</td>
                        <td className="py-2.5 px-3 font-mono text-slate-700">{doc.chunk_count}</td>
                        <td className="py-2.5 px-3">
                          <span className="inline-flex items-center space-x-1 text-[11px] text-emerald-700 font-medium">
                            <CheckCircle2 size={12} className="text-emerald-500" />
                            <span className="capitalize">{doc.status || 'Indexed'}</span>
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Subsystem Health Grid */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="flex items-center space-x-2 mb-4">
              <Activity size={17} className="text-indigo-600" />
              <h3 className="font-bold text-sm text-slate-900">Subsystem Operational Health</h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              {/* SQLite DB */}
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-slate-700">SQLite Database</span>
                  <CheckCircle2 size={14} className="text-emerald-500" />
                </div>
                <p className="text-[11px] text-slate-500">Document registry, chunks & logs</p>
                <div className="text-[10px] font-mono text-slate-600 mt-2 font-medium">Status: Connected</div>
              </div>

              {/* ChromaDB Vector Store */}
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-slate-700">ChromaDB Store</span>
                  <CheckCircle2 size={14} className="text-emerald-500" />
                </div>
                <p className="text-[11px] text-slate-500">all-MiniLM-L6-v2 embeddings</p>
                <div className="text-[10px] font-mono text-slate-600 mt-2 font-medium">
                  Status: {ragStatus?.total_chunks_indexed ?? 0} vectors
                </div>
              </div>

              {/* BM25 Sparse Indexer */}
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-slate-700">BM25 Okapi</span>
                  <CheckCircle2 size={14} className="text-emerald-500" />
                </div>
                <p className="text-[11px] text-slate-500">Lexical term matching & scoring</p>
                <div className="text-[10px] font-mono text-slate-600 mt-2 font-medium">Status: Active (3 versions)</div>
              </div>

              {/* LLM Engine */}
              <div className="p-3 rounded-lg border border-slate-200 bg-slate-50/60">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-slate-700">LLM Provider</span>
                  <Zap size={14} className="text-indigo-600" />
                </div>
                <p className="text-[11px] text-slate-500 capitalize">{activeProvider} ({activeModel})</p>
                <div className="text-[10px] font-mono text-slate-600 mt-2 font-medium">
                  Mode: {chatConfig?.api_key_configured ? 'API Online' : 'Extractive Fallback'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (1 col): Recent Chat Activity & Versions */}
        <div className="space-y-6">
          {/* Version Scope Distribution Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
            <h3 className="font-bold text-sm text-slate-900 mb-3 flex items-center space-x-2">
              <Cpu size={16} className="text-indigo-600" />
              <span>Multi-Version Isolation Scope</span>
            </h3>

            <div className="space-y-2.5">
              {['v1.0', 'v2.0', 'v3.0'].map((ver) => {
                const docCount = stats?.by_version?.[ver] ?? 0;
                const chunkCount = ragStatus?.by_version?.[ver] ?? 0;
                return (
                  <div
                    key={ver}
                    onClick={() => setSelectedVersion(ver)}
                    className={`p-2.5 rounded-lg border cursor-pointer transition-all ${
                      selectedVersion === ver
                        ? 'border-indigo-500 bg-indigo-50/40'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-slate-800">NexaDesk {ver}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-white text-indigo-700 border border-indigo-200">
                        {selectedVersion === ver ? 'Selected' : 'Select'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1">
                      <span>{docCount} documents</span>
                      <span className="font-mono">{chunkCount} indexed chunks</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Customer Activity */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-1.5">
                <MessageSquare size={16} className="text-indigo-600" />
                <h3 className="font-bold text-sm text-slate-900">Recent Customer Activity</h3>
              </div>
              <span className="text-[11px] font-mono text-slate-500">{recentEnquiries.length} logs</span>
            </div>

            {recentEnquiries.length === 0 ? (
              <div className="text-center py-6 text-slate-400 text-xs">
                No customer enquiry activity recorded yet.
              </div>
            ) : (
              <div className="space-y-2.5">
                {recentEnquiries.slice(0, 4).map((enq) => (
                  <div key={enq.id} className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/50 text-xs space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="font-semibold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
                        {enq.product_version}
                      </span>
                      <span>{enq.created_at ? new Date(enq.created_at).toLocaleTimeString() : 'Recent'}</span>
                    </div>
                    <p className="font-medium text-slate-800 truncate" title={enq.user_query}>
                      "{enq.user_query}"
                    </p>
                    <p className="text-[11px] text-slate-500 truncate" title={enq.response_text}>
                      {enq.response_text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
