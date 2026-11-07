import React from 'react';
import { Layers, Folder, Database, Check } from 'lucide-react';

export function SystemInfoCard({ systemInfo }) {
  if (!systemInfo) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center space-x-2 mb-4">
        <Layers className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-slate-900 text-base">Project Architecture & Versioning</h3>
      </div>

      <div className="space-y-4 text-xs">
        <div>
          <span className="text-slate-500 font-medium block mb-1">Project Name</span>
          <span className="font-semibold text-slate-800 text-sm">{systemInfo.project_name}</span>
        </div>

        <div>
          <span className="text-slate-500 font-medium block mb-1">Configured NexaDesk Versions</span>
          <div className="flex flex-wrap gap-2">
            {systemInfo.supported_product_versions?.map((ver) => (
              <span
                key={ver}
                className="px-2.5 py-1 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 font-semibold font-mono"
              >
                {ver} {ver === systemInfo.default_product_version && '(Default)'}
              </span>
            ))}
          </div>
        </div>

        <div>
          <span className="text-slate-500 font-medium block mb-1">RAG Pipeline Status</span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-100 text-slate-800 font-medium">
            <Check size={14} className="text-emerald-600" /> {systemInfo.rag_status}
          </span>
        </div>

        <div className="pt-2 border-t border-slate-100">
          <span className="text-slate-500 font-medium block mb-2">Storage Directory Mappings</span>
          <div className="space-y-1.5 font-mono text-[11px] text-slate-600">
            {Object.entries(systemInfo.storage_directories || {}).map(([key, val]) => (
              <div key={key} className="flex justify-between items-center py-1 px-2 rounded bg-slate-50">
                <span className="font-semibold text-slate-700">{key}:</span>
                <span className="text-slate-500 truncate max-w-xs">{val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SystemInfoCard;

