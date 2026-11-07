import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  UploadCloud,
  Trash2,
  RefreshCw,
  Search,
  Eye,
  Hash,
  X,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Database,
} from 'lucide-react';
import documentService from '../../services/documentService';
import ragService from '../../services/ragService';
import { useSystem } from '../../context/SystemContext';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Alert } from '../common/Alert';

export function DocumentExplorer() {
  const { selectedVersion } = useSystem();

  // State
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeVersionFilter, setActiveVersionFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [syncingVectors, setSyncingVectors] = useState(false);
  const [syncNotice, setSyncNotice] = useState(null);

  // Upload Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProductName, setUploadProductName] = useState('NexaDesk');
  const [uploadVersion, setUploadVersion] = useState(selectedVersion || 'v3.0');
  const [uploadCategory, setUploadCategory] = useState('Getting Started');
  const [uploadChunkSize, setUploadChunkSize] = useState(800);
  const [uploadChunkOverlap, setUploadChunkOverlap] = useState(150);
  const [replaceExisting, setReplaceExisting] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  // Document Details & Chunk Inspector Modal State
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
        text: `Vector store synchronized successfully (${res.chunks_indexed || 33} vectors indexed).`
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

  // Upload handler with FormData
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
        text: `Ingested '${res.document.document_name}' into ${res.chunks_created} vector chunks.`
      });
      setUploadFile(null);
      loadData();
      setTimeout(() => {
        setShowUploadModal(false);
        setUploadMessage(null);
      }, 1500);
    } catch (err) {
      setUploadMessage({
        type: err.status === 409 ? 'warning' : 'error',
        text: err.message || 'Upload failed. Check server logs.',
      });
    } finally {
      setUploading(false);
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setUploadFile(e.dataTransfer.files[0]);
    }
  };

  // Delete document
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

  // View Details & Chunks
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
    return (
      doc.document_name.toLowerCase().includes(q) ||
      doc.category.toLowerCase().includes(q) ||
      doc.product_version.toLowerCase().includes(q)
    );
  });

  // Small coloured file-type indicators (PDF Coral, DOCX Blue, TXT Amber, MD Violet)
  const getFormatBadge = (type) => {
    switch (type?.toLowerCase()) {
      case 'pdf':
        return 'bg-accent-coral/15 text-accent-coral border-accent-coral/25';
      case 'docx':
        return 'bg-accent-blue/15 text-accent-blue border-accent-blue/25';
      case 'md':
        return 'bg-accent-violet/15 text-accent-violet border-accent-violet/25';
      case 'txt':
        return 'bg-accent-amber/15 text-accent-amber border-accent-amber/25';
      default:
        return 'bg-white/[0.05] text-slate-300 border-white/[0.06]';
    }
  };

  // Subtle coloured version indicators
  const getVersionBadge = (ver) => {
    switch (ver) {
      case 'v1.0':
        return 'bg-accent-blue/15 text-accent-blue border-accent-blue/30';
      case 'v2.0':
        return 'bg-accent-violet/15 text-accent-violet border-accent-violet/30';
      case 'v3.0':
        return 'bg-accent-cyan/15 text-accent-cyan border-accent-cyan/30';
      default:
        return 'bg-white/[0.05] text-slate-300 border-white/[0.06]';
    }
  };

  return (
    <div className="space-y-6 text-slate-100">
      {/* 1. Header with Title, Compact Summary Metrics, and Prominent Upload Button */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Knowledge Base
          </h1>
          <p className="text-xs text-slate-300 mt-0.5">
            Manage multi-version enterprise documentation and vector indexes.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Compact Summary Metrics */}
          <div className="flex items-center space-x-2 bg-[#141E33] border border-white/[0.08] px-3 py-1.5 rounded-xl text-xs font-mono">
            <span className="text-slate-400">Docs:</span>
            <span className="font-bold text-white">{stats?.total_documents ?? 18}</span>
            <span className="text-white/20">·</span>
            <span className="text-slate-400">Chunks:</span>
            <span className="font-bold text-accent-blue">{stats?.total_chunks ?? 33}</span>
          </div>

          {/* Sync ChromaDB Button */}
          <button
            onClick={handleSyncVectors}
            disabled={syncingVectors}
            className="p-2 text-slate-400 hover:text-white hover:bg-white/[0.04] rounded-xl border border-white/[0.08] transition-colors"
            title="Synchronize ChromaDB vectors"
          >
            <RefreshCw size={14} className={syncingVectors ? 'animate-spin text-accent-blue' : ''} />
          </button>

          {/* Prominent Upload Button */}
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold text-xs shadow-glow-blue transition-all"
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

      {error && <Alert type="error" title="Knowledge Base Connection Error" message={error} onRetry={loadData} />}

      {/* 2. Compact Search & Version Filter Toolbar in One Clean Line */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-3 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Version Filter Tabs */}
        <div className="flex items-center space-x-1 overflow-x-auto pb-1 sm:pb-0">
          {['all', 'v1.0', 'v2.0', 'v3.0'].map((ver) => (
            <button
              key={ver}
              onClick={() => setActiveVersionFilter(ver)}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono font-medium transition-colors ${
                activeVersionFilter === ver
                  ? 'bg-accent-blue text-white shadow-sm font-semibold'
                  : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              {ver === 'all' ? 'All Versions' : `NexaDesk ${ver}`}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:max-w-xs">
          <Search size={14} className="absolute left-3.5 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents or categories..."
            className="w-full pl-9 pr-8 py-2 text-xs bg-[#192640] border border-white/[0.08] rounded-xl text-white placeholder:text-slate-400 focus:outline-none focus:border-accent-blue"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2.5 text-slate-400 hover:text-white"
            >
              <X size={13} />
            </button>
          )}
        </div>
      </div>

      {/* 3. Clean Document Table (Document Name, Version, Category, Chunks, Actions) */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] shadow-card overflow-hidden">
        {loading && !documents.length ? (
          <div className="p-12">
            <LoadingSpinner label="Loading knowledge base records from SQLite..." />
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <FileText className="w-8 h-8 mx-auto text-slate-500" />
            <p className="text-sm font-semibold text-white">No documentation files found.</p>
            <p className="text-xs text-slate-300 max-w-sm mx-auto">
              Try adjusting your version filter or upload a new product guide.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-white/[0.08] text-left text-xs">
              <thead className="bg-[#192640] text-slate-300 font-semibold text-[11px]">
                <tr>
                  <th className="px-5 py-3">Document Name</th>
                  <th className="px-4 py-3">Version</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Chunks</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04] text-white">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors">
                    {/* Document Name with File Type Indicator */}
                    <td className="px-5 py-3.5 flex items-center space-x-2.5">
                      <span className={`uppercase font-mono text-[9px] font-bold px-1.5 py-0.5 rounded border ${getFormatBadge(doc.document_type)} flex-shrink-0`}>
                        {doc.document_type}
                      </span>
                      <span className="font-medium text-white truncate max-w-xs sm:max-w-md" title={doc.document_name}>
                        {doc.document_name}
                      </span>
                    </td>

                    {/* Version Indicator */}
                    <td className="px-4 py-3.5 font-mono">
                      <span className={`px-2 py-0.5 rounded-md font-semibold border text-[11px] ${getVersionBadge(doc.product_version)}`}>
                        {doc.product_version}
                      </span>
                    </td>

                    {/* Category */}
                    <td className="px-4 py-3.5 text-slate-300">{doc.category}</td>

                    {/* Chunks */}
                    <td className="px-4 py-3.5 font-mono">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="text-accent-blue hover:text-accent-blue-light font-medium"
                        title="Inspect extracted chunks"
                      >
                        {doc.chunk_count} chunks
                      </button>
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-3.5 text-right space-x-1">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="p-1.5 text-slate-300 hover:text-white hover:bg-white/[0.04] rounded-lg transition-colors"
                        title="View details & chunks"
                      >
                        <Eye size={15} />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id, doc.document_name)}
                        className="p-1.5 text-slate-400 hover:text-accent-coral hover:bg-accent-coral/10 rounded-lg transition-colors"
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

      {/* 4. Elegant Upload Modal with Drag-and-Drop */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-[#070A14]/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-[#141E33] rounded-2xl shadow-modal max-w-lg w-full border border-white/[0.1] p-6 space-y-4 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-accent-blue/15 text-accent-blue border border-accent-blue/25">
                  <UploadCloud size={16} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Upload Documentation</h3>
                  <p className="text-xs text-slate-300">Ingest PDF, DOCX, TXT, or Markdown documents</p>
                </div>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]"
              >
                <X size={16} />
              </button>
            </div>

            {uploadMessage && (
              <Alert
                type={uploadMessage.type}
                title={uploadMessage.type === 'success' ? 'Upload Complete' : 'Notice'}
                message={uploadMessage.text}
              />
            )}

            <form onSubmit={handleUpload} className="space-y-4 text-xs">
              {/* Drag-and-Drop Area */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`p-6 border-2 border-dashed rounded-xl text-center cursor-pointer transition-colors ${
                  isDragging
                    ? 'border-accent-blue bg-accent-blue/10'
                    : uploadFile
                    ? 'border-accent-emerald/40 bg-accent-emerald/10'
                    : 'border-white/[0.1] hover:border-white/[0.2] bg-[#192640]/50'
                }`}
                onClick={() => document.getElementById('file-upload-input').click()}
              >
                <input
                  id="file-upload-input"
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={(e) => setUploadFile(e.target.files[0] || null)}
                  className="hidden"
                />
                <UploadCloud size={24} className={`mx-auto mb-2 ${uploadFile ? 'text-accent-emerald' : 'text-accent-blue'}`} />
                {uploadFile ? (
                  <div className="space-y-1">
                    <p className="font-semibold text-white text-xs">{uploadFile.name}</p>
                    <p className="text-[11px] text-slate-300 font-mono">{(uploadFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <p className="font-medium text-white text-xs">Drop documentation file here, or click to browse</p>
                    <p className="text-[11px] text-slate-400">Supports .pdf, .docx, .txt, .md</p>
                  </div>
                )}
              </div>

              {/* Version & Category Controls */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1">Target Version Scope</label>
                  <select
                    value={uploadVersion}
                    onChange={(e) => setUploadVersion(e.target.value)}
                    className="w-full bg-[#192640] border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-accent-blue"
                  >
                    <option value="v1.0">NexaDesk v1.0</option>
                    <option value="v2.0">NexaDesk v2.0</option>
                    <option value="v3.0">NexaDesk v3.0</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1">Category</label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    className="w-full bg-[#192640] border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-accent-blue"
                  >
                    <option value="Getting Started">Getting Started</option>
                    <option value="Integrations">Integrations</option>
                    <option value="Automation & Rules">Automation & Rules</option>
                    <option value="Pricing & Plans">Pricing & Plans</option>
                    <option value="Security & Compliance">Security & Compliance</option>
                  </select>
                </div>
              </div>

              {/* Chunking Settings */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1">Chunk Size (chars)</label>
                  <input
                    type="number"
                    value={uploadChunkSize}
                    onChange={(e) => setUploadChunkSize(Number(e.target.value))}
                    min={200}
                    max={2000}
                    className="w-full bg-[#192640] border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-accent-blue"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-slate-300 block mb-1">Overlap (chars)</label>
                  <input
                    type="number"
                    value={uploadChunkOverlap}
                    onChange={(e) => setUploadChunkOverlap(Number(e.target.value))}
                    min={0}
                    max={500}
                    className="w-full bg-[#192640] border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-accent-blue"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="replace-existing"
                  checked={replaceExisting}
                  onChange={(e) => setReplaceExisting(e.target.checked)}
                  className="rounded bg-[#192640] border-white/[0.1] text-accent-blue focus:ring-0"
                />
                <label htmlFor="replace-existing" className="text-slate-300 text-[11px] cursor-pointer">
                  Replace existing chunks if file name matches
                </label>
              </div>

              <div className="pt-2 flex justify-end space-x-2 border-t border-white/[0.08]">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 bg-[#192640] hover:bg-[#213354] text-slate-300 hover:text-white rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-4 py-2 bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold rounded-xl transition-all shadow-glow-blue disabled:opacity-50"
                >
                  {uploading ? 'Ingesting...' : 'Ingest Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 5. Document Details & Chunk Inspector Modal */}
      {inspectingDoc && (
        <div className="fixed inset-0 bg-[#070A14]/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-[#141E33] rounded-2xl shadow-modal max-w-2xl w-full border border-white/[0.1] p-6 space-y-4 text-white max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] flex-shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-accent-blue/15 text-accent-blue border border-accent-blue/25">
                  <FileText size={16} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white truncate max-w-sm">
                    {inspectingDoc.document_name}
                  </h3>
                  <span className="text-[11px] text-slate-300 font-mono">
                    Document Metadata & Vector Chunks
                  </span>
                </div>
              </div>
              <button
                onClick={() => setInspectingDoc(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]"
              >
                <X size={16} />
              </button>
            </div>

            {/* Secondary Metadata Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 bg-[#192640] p-3 rounded-xl border border-white/[0.08] text-xs font-mono flex-shrink-0">
              <div>
                <span className="text-slate-400 text-[10px] block">Version Scope</span>
                <span className="text-accent-blue font-semibold">{inspectingDoc.product_version}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">Category</span>
                <span className="text-white truncate block">{inspectingDoc.category}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">File Size</span>
                <span className="text-slate-300">{(inspectingDoc.file_size / 1024).toFixed(1)} KB</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] block">Ingested Date</span>
                <span className="text-slate-300">{new Date(inspectingDoc.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Extracted Chunks List */}
            <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
              <span className="text-xs font-semibold text-slate-200 block">
                Extracted Chunks ({chunks.length})
              </span>
              {loadingChunks ? (
                <div className="py-8">
                  <LoadingSpinner label="Loading vector chunks..." />
                </div>
              ) : chunks.length === 0 ? (
                <div className="py-6 text-center text-slate-400 text-xs">
                  No chunks recorded for this document.
                </div>
              ) : (
                chunks.map((chunk, idx) => (
                  <div key={chunk.id || idx} className="p-3 bg-[#192640] rounded-xl border border-white/[0.08] space-y-1.5 text-xs">
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                      <span className="text-white">Chunk #{idx + 1} {chunk.section_title ? `· ${chunk.section_title}` : ''}</span>
                      <span>Page {chunk.page_number} · {chunk.character_count || chunk.text_content?.length} chars</span>
                    </div>
                    <p className="text-slate-200 font-mono text-xs leading-relaxed whitespace-pre-wrap">
                      {chunk.text_content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-white/[0.08] flex justify-end flex-shrink-0">
              <button
                onClick={() => setInspectingDoc(null)}
                className="px-4 py-2 bg-[#192640] hover:bg-[#213354] text-white font-semibold rounded-xl text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentExplorer;
