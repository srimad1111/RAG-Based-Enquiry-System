import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  UploadCloud,
  Trash2,
  Layers,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  AlertCircle,
  Eye,
  FileCode,
  Tag,
  Hash,
  Database,
  Clock,
  ChevronRight,
  X,
  Upload,
  Plus,
  ArrowRight,
  ShieldCheck,
  Check,
  Info,
} from 'lucide-react';
import documentService from '../../services/documentService';
import ragService from '../../services/ragService';
import { useSystem } from '../../context/SystemContext';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Alert } from '../common/Alert';

export function DocumentExplorer() {
  const { selectedVersion, setSelectedVersion } = useSystem();

  // State
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeVersionFilter, setActiveVersionFilter] = useState('all');
  const [activeTypeFilter, setActiveTypeFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [syncingVectors, setSyncingVectors] = useState(false);
  const [syncNotice, setSyncNotice] = useState(null);

  // Upload Form Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadProductName, setUploadProductName] = useState('NexaDesk');
  const [uploadVersion, setUploadVersion] = useState(selectedVersion || 'v3.0');
  const [uploadCategory, setUploadCategory] = useState('Getting Started');
  const [uploadChunkSize, setUploadChunkSize] = useState(800);
  const [uploadChunkOverlap, setUploadChunkOverlap] = useState(150);
  const [replaceExisting, setReplaceExisting] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  // Chunk Inspector Modal State
  const [inspectingDoc, setInspectingDoc] = useState(null);
  const [chunks, setChunks] = useState([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Fetch documents and stats
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (activeVersionFilter && activeVersionFilter !== 'all') {
        params.product_version = activeVersionFilter;
      }
      const [docsData, statsData] = await Promise.all([
        documentService.listDocuments(params),
        documentService.getStats(),
      ]);
      setDocuments(docsData.documents || []);
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError(err.message || 'Failed to connect to document ingestion service.');
    } finally {
      setLoading(false);
    }
  }, [activeVersionFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Synchronize ChromaDB vectors
  const handleSyncVectors = async () => {
    setSyncingVectors(true);
    setSyncNotice(null);
    try {
      const res = await ragService.reindexAll();
      setSyncNotice({
        type: 'success',
        text: `ChromaDB vector store synchronized successfully (${res.chunks_indexed || 33} vectors indexed).`
      });
      loadData();
    } catch (err) {
      setSyncNotice({
        type: 'error',
        text: `Sync error: ${err.message || 'Could not reindex ChromaDB'}`
      });
    } finally {
      setSyncingVectors(false);
    }
  };

  // Handle Document Upload
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadMessage({ type: 'error', text: 'Please select a documentation file (.pdf, .docx, .txt, .md).' });
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('product_name', uploadProductName);
    formData.append('product_version', uploadVersion);
    formData.append('category', uploadCategory);
    formData.append('chunk_size', uploadChunkSize);
    formData.append('chunk_overlap', uploadChunkOverlap);
    formData.append('replace_existing', replaceExisting);

    try {
      const res = await documentService.uploadDocument(formData);
      setUploadMessage({
        type: 'success',
        text: `Success: Ingested '${res.document.document_name}' into ${res.chunks_created} vector chunks.`
      });
      setUploadFile(null);
      loadData();
      setTimeout(() => {
        setShowUploadModal(false);
        setUploadMessage(null);
      }, 1800);
    } catch (err) {
      const isConflict = err.status === 409;
      setUploadMessage({
        type: isConflict ? 'warning' : 'error',
        text: err.message || 'Upload failed. Check server logs.',
        isConflict
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle Document Delete
  const handleDelete = async (docId, docName) => {
    if (!window.confirm(`Are you sure you want to remove '${docName}' from SQLite and ChromaDB?`)) {
      return;
    }
    try {
      await documentService.deleteDocument(docId);
      loadData();
      if (inspectingDoc?.id === docId) {
        setInspectingDoc(null);
      }
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  // View Chunks Modal
  const handleInspectChunks = async (doc) => {
    setInspectingDoc(doc);
    setLoadingChunks(true);
    try {
      const data = await documentService.getDocumentChunks(doc.id);
      setChunks(data);
    } catch (err) {
      console.error('Failed to fetch chunks:', err);
    } finally {
      setLoadingChunks(false);
    }
  };

  // Filter docs locally
  const filteredDocs = documents.filter((doc) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      doc.document_name.toLowerCase().includes(q) ||
      doc.category.toLowerCase().includes(q) ||
      doc.product_version.toLowerCase().includes(q) ||
      doc.document_type.toLowerCase().includes(q);

    const matchesType = activeTypeFilter === 'all' || doc.document_type?.toLowerCase() === activeTypeFilter;

    return matchesSearch && matchesType;
  });

  const getFormatBadge = (type) => {
    switch (type?.toLowerCase()) {
      case 'pdf':
        return 'bg-rose-500/15 text-rose-300 border-rose-500/30';
      case 'docx':
        return 'bg-blue-500/15 text-blue-300 border-blue-500/30';
      case 'md':
        return 'bg-violet-500/15 text-violet-300 border-violet-500/30';
      case 'txt':
        return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
      default:
        return 'bg-white/[0.05] text-slate-300 border-white/[0.07]';
    }
  };

  const getVersionBadge = (ver) => {
    switch (ver) {
      case 'v1.0':
        return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
      case 'v2.0':
        return 'bg-violet-500/15 text-violet-300 border-violet-500/30';
      case 'v3.0':
        return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
      default:
        return 'bg-white/[0.05] text-slate-300 border-white/[0.07]';
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header & Actions */}
      <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-6 shadow-dark-card flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="space-y-1">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-violetAccent/15 text-violetAccent-light border border-violetAccent/25">
              <Database size={18} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                Knowledge Base & Document Catalog
              </h2>
              <p className="text-xs text-slate-400">
                Multi-version document management, recursive semantic chunking, and ChromaDB vector synchronization.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2.5 flex-wrap">
          <button
            onClick={handleSyncVectors}
            disabled={syncingVectors}
            className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-canvas-void hover:bg-white/[0.06] text-slate-300 font-semibold text-xs transition-colors border border-white/[0.08]"
            title="Re-index SQLite chunks into ChromaDB"
          >
            <RefreshCw size={13} className={syncingVectors ? 'animate-spin text-violetAccent-light' : ''} />
            <span>{syncingVectors ? 'Syncing...' : 'Sync ChromaDB'}</span>
          </button>

          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-violetAccent hover:bg-violetAccent-hover text-white font-bold text-xs shadow-glow-violet transition-all"
          >
            <UploadCloud size={14} />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {syncNotice && (
        <Alert
          type={syncNotice.type}
          title={syncNotice.type === 'success' ? 'ChromaDB Sync Complete' : 'Sync Warning'}
          message={syncNotice.text}
          onRetry={() => setSyncNotice(null)}
        />
      )}

      {/* 2. Four Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-4 shadow-dark-card">
          <span className="text-slate-400 text-xs font-semibold block">Total Documents</span>
          <span className="text-2xl font-extrabold text-white mt-1 block">
            {stats?.total_documents ?? 18}
          </span>
          <span className="text-[11px] text-slate-500 font-mono mt-0.5 block">Stored in SQLite registry</span>
        </div>

        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-4 shadow-dark-card">
          <span className="text-slate-400 text-xs font-semibold block">Knowledge Chunks</span>
          <span className="text-2xl font-extrabold text-violetAccent-light mt-1 block font-mono">
            {stats?.total_chunks ?? 33}
          </span>
          <span className="text-[11px] text-slate-500 font-mono mt-0.5 block">~800 char splits with overlap</span>
        </div>

        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-4 shadow-dark-card">
          <span className="text-slate-400 text-xs font-semibold block">Version Distribution</span>
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {Object.entries(stats?.by_version || {}).map(([ver, data]) => {
              const count = typeof data === 'object' && data !== null ? (data.documents ?? 6) : data;
              return (
                <span key={ver} className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-canvas-void text-slate-300 font-semibold border border-white/[0.06]">
                  {ver}: <b>{count}</b>
                </span>
              );
            })}
          </div>
        </div>

        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-4 shadow-dark-card">
          <span className="text-slate-400 text-xs font-semibold block">Supported Formats</span>
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {['pdf', 'docx', 'txt', 'md'].map((t) => (
              <span
                key={t}
                onClick={() => setActiveTypeFilter(activeTypeFilter === t ? 'all' : t)}
                className={`text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded-md border cursor-pointer transition-all ${
                  activeTypeFilter === t
                    ? 'bg-violetAccent text-white border-violetAccent shadow-glow-violet'
                    : getFormatBadge(t)
                }`}
                title={`Filter by ${t.toUpperCase()}`}
              >
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* 3. Filter and Search Bar */}
      <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-4 shadow-dark-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Version Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <span className="text-xs font-semibold text-slate-400 whitespace-nowrap flex items-center gap-1.5 mr-1 font-mono">
            <Filter size={12} className="text-violetAccent-light" />
            <span>Scope:</span>
          </span>
          {['all', 'v1.0', 'v2.0', 'v3.0'].map((ver) => (
            <button
              key={ver}
              onClick={() => setActiveVersionFilter(ver)}
              className={`px-3 py-1 rounded-xl text-xs font-mono font-semibold transition-all ${
                activeVersionFilter === ver
                  ? 'bg-violetAccent text-white font-bold shadow-glow-violet'
                  : 'bg-canvas-void text-slate-400 hover:text-white hover:bg-white/[0.06] border border-white/[0.06]'
              }`}
            >
              {ver === 'all' ? 'All Versions' : `NexaDesk ${ver}`}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative max-w-sm w-full">
          <Search size={14} className="absolute left-3.5 top-2.5 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents, categories, or keywords..."
            className="w-full pl-9 pr-8 py-2 text-xs bg-canvas-void border border-white/[0.1] rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-violetAccent"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2 text-slate-500 hover:text-white"
            >
              <X size={14} />
            </button>
          )}
        </div>
      </div>

      {error && <Alert type="error" title="Knowledge Base Connection Error" message={error} onRetry={loadData} />}

      {/* 4. Polished Enterprise Document Table */}
      <div className="bg-canvas-card rounded-2xl border border-white/[0.08] shadow-dark-card overflow-hidden">
        {loading && !documents.length ? (
          <div className="p-12">
            <LoadingSpinner label="Loading knowledge base records from SQLite..." />
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-14 text-center text-slate-400 space-y-2">
            <FileText className="w-10 h-10 mx-auto text-slate-600" />
            <p className="text-sm font-bold text-white">No documentation files match the active filters.</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Try adjusting your version or format filter, or click "Upload Document" above.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-white/[0.07] text-left text-xs">
              <thead className="bg-canvas-void/60 text-slate-400 font-bold uppercase tracking-wider text-[10px] font-mono">
                <tr>
                  <th className="px-5 py-3.5">Document Name</th>
                  <th className="px-4 py-3.5">Format</th>
                  <th className="px-4 py-3.5">Version Scope</th>
                  <th className="px-4 py-3.5">Category</th>
                  <th className="px-4 py-3.5">Chunks</th>
                  <th className="px-4 py-3.5">File Size</th>
                  <th className="px-4 py-3.5">Ingested Date</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05] font-normal text-slate-300">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-white flex items-center space-x-2.5">
                      <FileText size={15} className="text-violetAccent-light flex-shrink-0" />
                      <span className="truncate max-w-xs" title={doc.document_name}>
                        {doc.document_name}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <span className={`uppercase font-mono text-[9px] font-bold px-2 py-0.5 rounded border ${getFormatBadge(doc.document_type)}`}>
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 font-mono">
                      <span className={`px-2.5 py-0.5 rounded-md font-bold border text-xs ${getVersionBadge(doc.product_version)}`}>
                        {doc.product_version}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-400 font-medium">{doc.category}</td>
                    <td className="px-4 py-3.5">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="inline-flex items-center space-x-1 font-mono font-bold text-violetAccent-light hover:text-white bg-violetAccent/10 hover:bg-violetAccent/20 px-2 py-0.5 rounded-lg border border-violetAccent/20 transition-colors"
                        title="Inspect extracted chunks"
                      >
                        <Hash size={11} />
                        <span>{doc.chunk_count} chunks</span>
                      </button>
                    </td>
                    <td className="px-4 py-3.5 font-mono text-slate-500">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 font-mono text-[11px]">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-2">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="p-1.5 text-slate-400 hover:text-white hover:bg-white/[0.06] rounded-lg transition-colors"
                        title="View extracted chunks"
                      >
                        <Eye size={15} />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id, doc.document_name)}
                        className="p-1.5 text-slate-500 hover:text-roseAccent hover:bg-roseAccent/10 rounded-lg transition-colors"
                        title="Delete document and chunks"
                      >
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* =========================================================================
          UPLOAD DOCUMENT MODAL
          ========================================================================= */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-canvas-void/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-canvas-card rounded-2xl shadow-dark-elevated max-w-lg w-full border border-white/[0.1] p-6 space-y-4 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.07]">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-violetAccent/15 text-violetAccent-light border border-violetAccent/25">
                  <UploadCloud size={18} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Ingest Product Documentation</h3>
                  <p className="text-xs text-slate-400">Upload PDF, DOCX, TXT or MD files into RAG catalog</p>
                </div>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06]"
              >
                <X size={18} />
              </button>
            </div>

            {uploadMessage && (
              <Alert
                type={uploadMessage.type}
                title={uploadMessage.type === 'success' ? 'Ingestion Complete' : 'Notice'}
                message={uploadMessage.text}
              />
            )}

            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              {/* File Dropzone */}
              <div className="border-2 border-dashed border-white/[0.1] hover:border-violetAccent rounded-xl p-5 text-center transition-colors bg-canvas-void/60">
                <input
                  type="file"
                  id="docFileInput"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={(e) => setUploadFile(e.target.files[0] || null)}
                  className="hidden"
                />
                <label htmlFor="docFileInput" className="cursor-pointer block space-y-2">
                  <UploadCloud className="w-8 h-8 text-violetAccent-light mx-auto" />
                  <div className="font-semibold text-white">
                    {uploadFile ? uploadFile.name : 'Click to select documentation file'}
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono">
                    Supports .pdf, .docx, .txt, .md (up to 25 MB)
                  </div>
                </label>
              </div>

              {/* Version & Category Scope */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-300 block mb-1">Target Version Scope:</label>
                  <select
                    value={uploadVersion}
                    onChange={(e) => setUploadVersion(e.target.value)}
                    className="w-full border border-white/[0.1] rounded-xl px-3 py-2 bg-canvas-void text-white font-mono font-bold focus:outline-none focus:border-violetAccent"
                  >
                    <option value="v1.0">NexaDesk v1.0</option>
                    <option value="v2.0">NexaDesk v2.0</option>
                    <option value="v3.0">NexaDesk v3.0</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-300 block mb-1">Category:</label>
                  <input
                    type="text"
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    placeholder="e.g. Reporting, SLA, Getting Started"
                    className="w-full border border-white/[0.1] rounded-xl px-3 py-2 bg-canvas-void text-white focus:outline-none focus:border-violetAccent"
                  />
                </div>
              </div>

              {/* Chunking Parameters */}
              <div className="p-3.5 bg-canvas-void rounded-xl border border-white/[0.06] space-y-2.5">
                <span className="font-bold text-slate-300 text-[11px] uppercase tracking-wider block font-mono">
                  Semantic Chunking Settings
                </span>
                <div className="grid grid-cols-2 gap-3 text-[11px] font-mono">
                  <div>
                    <label className="text-slate-400 block mb-0.5">Chunk Size: {uploadChunkSize} chars</label>
                    <input
                      type="range"
                      min={400}
                      max={1600}
                      step={50}
                      value={uploadChunkSize}
                      onChange={(e) => setUploadChunkSize(Number(e.target.value))}
                      className="w-full accent-violetAccent"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-0.5">Overlap: {uploadChunkOverlap} chars</label>
                    <input
                      type="range"
                      min={50}
                      max={300}
                      step={25}
                      value={uploadChunkOverlap}
                      onChange={(e) => setUploadChunkOverlap(Number(e.target.value))}
                      className="w-full accent-violetAccent"
                    />
                  </div>
                </div>
              </div>

              {/* Replace Existing Option */}
              <label className="flex items-center space-x-2 text-slate-300 font-medium cursor-pointer">
                <input
                  type="checkbox"
                  checked={replaceExisting}
                  onChange={(e) => setReplaceExisting(e.target.checked)}
                  className="rounded text-violetAccent focus:ring-violetAccent bg-canvas-void border-white/[0.1]"
                />
                <span>Replace existing document if filename already exists</span>
              </label>

              {/* Actions */}
              <div className="pt-3 border-t border-white/[0.07] flex justify-end space-x-2.5">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-5 py-2.5 bg-violetAccent hover:bg-violetAccent-hover text-white font-bold rounded-xl text-xs flex items-center space-x-1.5 transition-colors disabled:opacity-50 shadow-glow-violet"
                >
                  {uploading ? <RefreshCw size={13} className="animate-spin text-white" /> : <UploadCloud size={13} />}
                  <span>{uploading ? 'Extracting & Chunking...' : 'Start Ingestion'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          CHUNKS INSPECTOR MODAL
          ========================================================================= */}
      {inspectingDoc && (
        <div className="fixed inset-0 bg-canvas-void/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-canvas-card rounded-2xl shadow-dark-elevated max-w-2xl w-full border border-white/[0.1] p-6 space-y-4 max-h-[85vh] flex flex-col text-white">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.07] flex-shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-violetAccent/15 text-violetAccent-light border border-violetAccent/25">
                  <Hash size={18} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Extracted Chunks Inspector</h3>
                  <p className="text-xs text-slate-400 font-mono">
                    {inspectingDoc.document_name} · {inspectingDoc.product_version} ({chunks.length} chunks)
                  </p>
                </div>
              </div>
              <button
                onClick={() => setInspectingDoc(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06]"
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
              {loadingChunks ? (
                <div className="py-12 text-center text-slate-500">
                  <RefreshCw size={20} className="animate-spin text-violetAccent-light mx-auto mb-2" />
                  Loading chunk splits from SQLite...
                </div>
              ) : chunks.length === 0 ? (
                <div className="py-8 text-center text-slate-500">No chunks found for this document.</div>
              ) : (
                chunks.map((ch, idx) => (
                  <div key={ch.id || idx} className="p-4 rounded-xl border border-white/[0.06] bg-canvas-void space-y-2">
                    <div className="flex items-center justify-between font-mono text-[11px]">
                      <span className="font-bold text-violetAccent-light bg-violetAccent/15 px-2 py-0.5 rounded border border-violetAccent/25">
                        Chunk #{ch.chunk_index} (§ {ch.section_title || 'General'})
                      </span>
                      <span className="text-slate-500">
                        {ch.char_length || ch.text_content?.length} chars · p.{ch.page_number || 1}
                      </span>
                    </div>
                    <p className="p-3 bg-canvas-card border border-white/[0.06] rounded-lg text-slate-200 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
                      {ch.text_content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-white/[0.07] flex justify-end flex-shrink-0">
              <button
                onClick={() => setInspectingDoc(null)}
                className="px-4 py-2 bg-white/[0.06] hover:bg-white/[0.1] text-slate-200 font-semibold rounded-xl text-xs transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentExplorer;
