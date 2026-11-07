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
  X
} from 'lucide-react';
import documentService from '../../services/documentService';
import { useSystem } from '../../context/SystemContext';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Alert } from '../common/Alert';
import { Badge } from '../common/Badge';

export function DocumentExplorer() {
  const { selectedVersion, setSelectedVersion } = useSystem();

  // State
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeVersionFilter, setActiveVersionFilter] = useState(selectedVersion || 'all');
  const [searchQuery, setSearchQuery] = useState('');

  // Upload Form Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadProductName, setUploadProductName] = useState('NexaDesk');
  const [uploadVersion, setUploadVersion] = useState(selectedVersion || 'v3.0');
  const [uploadCategory, setUploadCategory] = useState('User Guide');
  const [uploadChunkSize, setUploadChunkSize] = useState(800);
  const [uploadChunkOverlap, setUploadChunkOverlap] = useState(150);
  const [replaceExisting, setReplaceExisting] = useState(false);
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

  // Handle Document Upload
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadMessage({ type: 'error', text: 'Please select a file (.pdf, .docx, .txt, .md).' });
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
        text: `Success: Ingested '${res.document.document_name}' into ${res.chunks_created} chunks.`
      });
      setUploadFile(null);
      // Refresh list
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
    if (!window.confirm(`Are you sure you want to delete '${docName}' and all its extracted chunks?`)) {
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

  // Filter docs locally by search query
  const filteredDocs = documents.filter((doc) => {
    const q = searchQuery.toLowerCase();
    return (
      doc.document_name.toLowerCase().includes(q) ||
      doc.category.toLowerCase().includes(q) ||
      doc.product_version.toLowerCase().includes(q) ||
      doc.document_type.toLowerCase().includes(q)
    );
  });

  const getFormatBadge = (type) => {
    switch (type?.toLowerCase()) {
      case 'pdf':
        return 'bg-rose-100 text-rose-700 border-rose-200';
      case 'docx':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'md':
        return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'txt':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Database className="w-6 h-6 text-indigo-600" />
            <h2 className="text-xl font-bold text-slate-900">Document Ingestion & Chunking Management</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Phase 2 Pipeline: PyMuPDF PDF parser, python-docx, Markdown & TXT recursive chunking with SQLite storage.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <UploadCloud size={16} />
            <span>Upload Document</span>
          </button>
          <button
            onClick={loadData}
            title="Refresh Ingestion Records"
            className="p-2 text-slate-500 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors border border-slate-200"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-500 text-xs font-medium block">Total Documents</span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">
            {stats?.total_documents ?? '...'}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">Indexed in SQLite</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-500 text-xs font-medium block">Structured Chunks</span>
          <span className="text-2xl font-bold text-indigo-600 mt-1 block font-mono">
            {stats?.total_chunks ?? '...'}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">~800 char splits with overlap</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-500 text-xs font-medium block">Version Distribution</span>
          <div className="flex items-center gap-2 mt-2">
            {Object.entries(stats?.by_version || {}).map(([ver, data]) => (
              <span key={ver} className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                {ver}: <b>{data.documents}</b>
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-slate-500 text-xs font-medium block">Supported Formats</span>
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {['pdf', 'docx', 'txt', 'md'].map((t) => (
              <span key={t} className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${getFormatBadge(t)}`}>
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
          <span className="text-xs text-slate-500 font-medium whitespace-nowrap flex items-center gap-1">
            <Filter size={13} /> Filter Version:
          </span>
          {['all', 'v1.0', 'v2.0', 'v3.0'].map((ver) => (
            <button
              key={ver}
              onClick={() => setActiveVersionFilter(ver)}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition-colors ${
                activeVersionFilter === ver
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {ver === 'all' ? 'All Versions' : ver}
            </button>
          ))}
        </div>

        <div className="relative max-w-xs w-full">
          <Search size={14} className="absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents or categories..."
            className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Error alert */}
      {error && <Alert type="error" title="Ingestion API Error" message={error} onRetry={loadData} />}

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading && !documents.length ? (
          <LoadingSpinner label="Loading ingested documents from SQLite..." />
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <FileText className="w-10 h-10 mx-auto text-slate-300 mb-2" />
            <p className="text-sm font-medium">No ingested documents found.</p>
            <p className="text-xs text-slate-400 mt-1">
              Upload a PDF, DOCX, TXT or MD file above or run the batch ingestion script.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Document Name</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Version</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Chunks</th>
                  <th className="px-4 py-3">File Size</th>
                  <th className="px-4 py-3">Ingested At</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-normal text-slate-700">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-4 py-3 font-semibold text-slate-900 flex items-center space-x-2">
                      <FileText size={16} className="text-slate-400 flex-shrink-0" />
                      <span className="truncate max-w-xs" title={doc.document_name}>{doc.document_name}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`uppercase font-mono text-[10px] font-bold px-2 py-0.5 rounded border ${getFormatBadge(doc.document_type)}`}>
                        {doc.document_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono font-semibold">
                      <span className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                        {doc.product_version}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{doc.category}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="inline-flex items-center gap-1 font-mono font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-0.5 rounded border border-indigo-200 transition-colors"
                        title="Inspect chunks"
                      >
                        <Hash size={12} />
                        <span>{doc.chunk_count} chunks</span>
                      </button>
                    </td>
                    <td className="px-4 py-3 font-mono text-slate-500">
                      {(doc.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-4 py-3 text-slate-400 text-[11px]">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <button
                        onClick={() => handleInspectChunks(doc)}
                        className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
                        title="View extracted chunks"
                      >
                        <Eye size={15} />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id, doc.document_name)}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
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

      {/* ============================================================================== */}
      {/* Upload Document Modal */}
      {/* ============================================================================== */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center space-x-2">
                <UploadCloud className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-slate-900 text-sm">Upload Company Documentation</h3>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleUpload} className="p-6 space-y-4 text-xs">
              {/* File selector */}
              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Document File (.pdf, .docx, .txt, .md) *
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt,.md,.markdown"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer border border-slate-200 rounded-lg p-1"
                  required
                />
              </div>

              {/* Product and Version */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Product Name *</label>
                  <input
                    type="text"
                    value={uploadProductName}
                    onChange={(e) => setUploadProductName(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Release Version *</label>
                  <select
                    value={uploadVersion}
                    onChange={(e) => setUploadVersion(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white font-mono font-semibold"
                    required
                  >
                    <option value="v1.0">v1.0</option>
                    <option value="v2.0">v2.0</option>
                    <option value="v3.0">v3.0</option>
                  </select>
                </div>
              </div>

              {/* Category */}
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Documentation Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white"
                >
                  <option value="User Guide">User Guide</option>
                  <option value="SLA & Protocols">SLA & Protocols</option>
                  <option value="Pricing & Billing">Pricing & Billing</option>
                  <option value="Access Control & Roles">Access Control & Roles</option>
                  <option value="AI & Enterprise Security">AI & Enterprise Security</option>
                  <option value="Visual Workflows">Visual Workflows</option>
                  <option value="API & Integrations">API & Integrations</option>
                  <option value="General">General</option>
                </select>
              </div>

              {/* Chunking parameters */}
              <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Chunk Size (chars)</label>
                  <input
                    type="number"
                    value={uploadChunkSize}
                    onChange={(e) => setUploadChunkSize(Number(e.target.value))}
                    min={200}
                    max={2000}
                    className="w-full border border-slate-300 rounded p-1.5 font-mono text-xs"
                  />
                </div>
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Chunk Overlap (chars)</label>
                  <input
                    type="number"
                    value={uploadChunkOverlap}
                    onChange={(e) => setUploadChunkOverlap(Number(e.target.value))}
                    min={0}
                    max={400}
                    className="w-full border border-slate-300 rounded p-1.5 font-mono text-xs"
                  />
                </div>
              </div>

              {/* Replace existing checkbox */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="replaceCheck"
                  checked={replaceExisting}
                  onChange={(e) => setReplaceExisting(e.target.checked)}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="replaceCheck" className="text-slate-600 text-xs">
                  Overwrite / Replace if this document was uploaded previously
                </label>
              </div>

              {/* Message */}
              {uploadMessage && (
                <div
                  className={`p-3 rounded-lg text-xs flex items-start gap-2 ${
                    uploadMessage.type === 'success'
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : uploadMessage.isConflict
                      ? 'bg-amber-50 text-amber-800 border border-amber-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}
                >
                  {uploadMessage.type === 'success' ? (
                    <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle size={16} className="text-rose-600 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p>{uploadMessage.text}</p>
                    {uploadMessage.isConflict && (
                      <button
                        type="button"
                        onClick={() => {
                          setReplaceExisting(true);
                          setUploadMessage(null);
                        }}
                        className="mt-2 underline font-semibold text-amber-900 block"
                      >
                        Click here to enable 'Overwrite' and retry
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Action buttons */}
              <div className="pt-2 flex justify-end space-x-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold rounded-lg shadow-sm transition-colors flex items-center space-x-1.5"
                >
                  {uploading ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      <span>Ingesting & Chunking...</span>
                    </>
                  ) : (
                    <span>Process & Ingest Document</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ============================================================================== */}
      {/* Chunk Inspector Modal */}
      {/* ============================================================================== */}
      {inspectingDoc && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-3xl w-full border border-slate-200 max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Header */}
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <Hash className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-bold text-slate-900 text-sm">
                    Structured Chunks Inspector: {inspectingDoc.document_name}
                  </h3>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Version: <span className="font-mono font-semibold text-indigo-700">{inspectingDoc.product_version}</span> | Total Chunks: {inspectingDoc.chunk_count}
                </p>
              </div>
              <button
                onClick={() => setInspectingDoc(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            {/* Chunk list body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
              {loadingChunks ? (
                <LoadingSpinner label="Loading chunk texts and metadata from SQLite..." />
              ) : chunks.length === 0 ? (
                <p className="text-center text-xs text-slate-400 py-8">No chunks found for this document.</p>
              ) : (
                chunks.map((chunk) => (
                  <div
                    key={chunk.id}
                    className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-indigo-300 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-100 text-[11px]">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                          Chunk #{chunk.chunk_index}
                        </span>
                        <span className="font-semibold text-slate-700">
                          Section: {chunk.section_title || 'General'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-3 text-slate-400 font-mono">
                        {chunk.page_number && <span>Page: {chunk.page_number}</span>}
                        <span>{chunk.char_count} chars</span>
                        <span className="text-slate-300 truncate max-w-[120px]">{chunk.id}</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
                      {chunk.text_content}
                    </p>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-slate-200 bg-white flex justify-between items-center text-xs text-slate-500">
              <span>Ready for Phase 3 vector embedding and BM25 indexation.</span>
              <button
                onClick={() => setInspectingDoc(null)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition-colors"
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
