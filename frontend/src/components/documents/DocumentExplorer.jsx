import React, { useState } from 'react';
import { FileText, FolderOpen, RefreshCw, Layers } from 'lucide-react';
import { useDocuments } from '../../hooks/useDocuments';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Alert } from '../common/Alert';
import { useSystem } from '../../context/SystemContext';

export function DocumentExplorer() {
  const { overview, loading, error, refreshDocuments } = useDocuments();
  const { selectedVersion, setSelectedVersion } = useSystem();
  const [activeFile, setActiveFile] = useState(null);

  if (loading) return <LoadingSpinner label="Scanning NexaDesk document directories..." />;
  if (error) return <Alert type="error" title="Documentation Catalog Error" message={error} onRetry={refreshDocuments} />;

  const currentVersionSummary = overview?.versions?.find((v) => v.version === selectedVersion) || overview?.versions?.[0];

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <FolderOpen className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">NexaDesk Multi-Version Document Catalog</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Grounded documentation source files across product release versions for Phase 2 RAG indexing.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-500 font-medium">Total Documents: </span>
          <span className="px-2.5 py-1 bg-indigo-50 text-indigo-700 font-bold rounded-full text-xs">
            {overview?.total_documents || 0} Files
          </span>
          <button
            onClick={refreshDocuments}
            className="p-2 text-slate-500 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Rescan Directories"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Version Tabs and File Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Version Summaries Column */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
            <Layers size={16} className="text-indigo-600" /> Release Versions
          </h3>
          <div className="space-y-3">
            {overview?.versions?.map((v) => {
              const isSelected = selectedVersion === v.version;
              return (
                <div
                  key={v.version}
                  onClick={() => {
                    setSelectedVersion(v.version);
                    setActiveFile(null);
                  }}
                  className={`cursor-pointer p-4 rounded-xl border transition-all ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/50 shadow-sm'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm text-slate-900 font-mono">NexaDesk {v.version}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium">
                      {v.file_count} documents
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 truncate font-mono mt-2">
                    .../{v.directory_path.split(/[/\\]/).slice(-3).join('/')}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* File Explorer Column */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Documentation Files ({selectedVersion})
              </h3>
              <p className="text-xs text-slate-500">
                Parsed and segmented into vector embeddings during Phase 2.
              </p>
            </div>
            <span className="text-xs font-mono font-semibold px-2 py-1 rounded bg-slate-100 text-slate-700">
              {currentVersionSummary?.files?.length || 0} markdown files
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {currentVersionSummary?.files?.map((filename) => (
              <div
                key={filename}
                onClick={() => setActiveFile(filename)}
                className={`p-3 rounded-lg border text-left cursor-pointer transition-colors flex items-start space-x-3 ${
                  activeFile === filename
                    ? 'border-indigo-500 bg-indigo-50/30'
                    : 'border-slate-200 hover:border-indigo-200 hover:bg-slate-50'
                }`}
              >
                <FileText className="w-5 h-5 text-indigo-500 flex-shrink-0 mt-0.5" />
                <div className="overflow-hidden">
                  <p className="text-xs font-semibold text-slate-800 truncate">{filename}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">Markdown Document</p>
                </div>
              </div>
            ))}
          </div>

          {activeFile && (
            <div className="mt-6 p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-semibold text-slate-700">File: {activeFile}</span>
                <span className="text-[11px] text-slate-400">Target for Phase 2 Chunking</span>
              </div>
              <p className="text-xs text-slate-600">
                Selected document is registered in the file system for NexaDesk {selectedVersion}.
                In Phase 2, this file will be parsed with LangChain RecursiveCharacterTextSplitter and indexed into ChromaDB with BM25 sparse tokens.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DocumentExplorer;

