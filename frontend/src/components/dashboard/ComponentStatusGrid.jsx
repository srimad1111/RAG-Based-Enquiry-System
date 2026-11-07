import React from 'react';
import { Server, Database, HardDrive, Sparkles, FolderCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { Badge } from '../common/Badge';

export function ComponentStatusGrid({ components }) {
  if (!components) return null;

  const getIcon = (key) => {
    switch (key) {
      case 'api_core':
        return <Server className="w-5 h-5 text-indigo-600" />;
      case 'sqlite_database':
        return <Database className="w-5 h-5 text-emerald-600" />;
      case 'chroma_storage':
        return <HardDrive className="w-5 h-5 text-purple-600" />;
      case 'file_storage':
        return <FolderCheck className="w-5 h-5 text-blue-600" />;
      case 'gemini_api':
        return <Sparkles className="w-5 h-5 text-amber-600" />;
      default:
        return <Server className="w-5 h-5 text-slate-600" />;
    }
  };

  const getLabel = (key) => {
    switch (key) {
      case 'api_core':
        return 'FastAPI Core Engine';
      case 'sqlite_database':
        return 'SQLite Database & Logs';
      case 'chroma_storage':
        return 'ChromaDB Local Vector Storage';
      case 'file_storage':
        return 'Multi-Version File System';
      case 'gemini_api':
        return 'Gemini LLM Provider';
      default:
        return key.replace(/_/g, ' ');
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="font-semibold text-slate-900 text-base mb-1">Subsystem Health Diagnostics</h3>
      <p className="text-xs text-slate-500 mb-4">Real-time status of backend services and persistent storage</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(components).map(([key, item]) => {
          const isOk = item.status === 'healthy';
          return (
            <div
              key={key}
              className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 hover:bg-slate-50 transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getIcon(key)}
                    <span className="font-semibold text-sm text-slate-800">{getLabel(key)}</span>
                  </div>
                  <Badge status={item.status} />
                </div>
                <p className="text-xs text-slate-600 mt-1">{item.message}</p>
              </div>

              {item.details && (
                <div className="mt-3 pt-2 border-t border-slate-200/70 text-[11px] font-mono text-slate-500 overflow-hidden text-ellipsis whitespace-nowrap">
                  {key === 'chroma_storage' && item.details.persist_directory && (
                    <span>Path: .../{item.details.persist_directory.split(/[/\\]/).slice(-2).join('/')}</span>
                  )}
                  {key === 'gemini_api' && (
                    <span>Model: {item.details.model}</span>
                  )}
                  {key === 'sqlite_database' && item.details.db_path && (
                    <span>DB: .../{item.details.db_path.split(/[/\\]/).slice(-2).join('/')}</span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ComponentStatusGrid;

