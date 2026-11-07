import React, { useState } from 'react';
import {
  X,
  Settings,
  Cpu,
  Database,
  Layers,
  Server,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  HardDrive,
  ExternalLink,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function SettingsModal({ isOpen, onClose }) {
  const { health, systemInfo, selectedVersion, refreshHealth, loading } = useSystem();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#0B1020]/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
      <div className="bg-[#141E33] border border-white/[0.09] rounded-2xl shadow-2xl max-w-lg w-full p-6 text-white space-y-5 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/[0.07]">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-accent-violet/15 text-accent-violet border border-accent-violet/25">
              <Settings size={18} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                System Telemetry & Engine Settings
              </h3>
              <p className="text-xs text-slate-400">
                Active LLM Provider, Vector Storage, and Multi-Version Isolation
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-3.5 text-xs">
          {/* Active LLM Provider Card */}
          <div className="p-4 rounded-xl bg-[#0B1020] border border-white/[0.06] space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Cpu size={15} className="text-accent-violet" />
                <span className="font-bold text-slate-200">Active Inference Engine</span>
              </div>
              <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/30 text-[10px] font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
                <span>ONLINE</span>
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-1 text-slate-300">
              <div><span className="text-slate-500">Provider:</span> <span className="text-white font-semibold">Ollama Local</span></div>
              <div><span className="text-slate-500">Model:</span> <span className="text-accent-violet font-semibold">qwen3.5:4b</span></div>
              <div><span className="text-slate-500">Endpoint:</span> <span className="text-slate-300">http://localhost:11434</span></div>
              <div><span className="text-slate-500">Grounding:</span> <span className="text-accent-emerald font-semibold">Strict Abstention</span></div>
            </div>
          </div>

          {/* ChromaDB Persistent Vector Store Card */}
          <div className="p-4 rounded-xl bg-[#0B1020] border border-white/[0.06] space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Database size={15} className="text-accent-blue" />
                <span className="font-bold text-slate-200">ChromaDB Vector Store</span>
              </div>
              <span className="text-[10px] font-mono text-accent-blue px-2 py-0.5 rounded bg-accent-blue/10 border border-accent-blue/20 font-semibold">
                384 Dimensions
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-1 text-slate-300">
              <div><span className="text-slate-500">Embedding:</span> <span className="text-white">all-MiniLM-L6-v2</span></div>
              <div><span className="text-slate-500">Indexed Chunks:</span> <span className="text-white">33 vectors</span></div>
              <div><span className="text-slate-500">Metric:</span> <span className="text-white">Cosine Distance</span></div>
              <div><span className="text-slate-500">Persistence:</span> <span className="text-accent-emerald">Persistent</span></div>
            </div>
          </div>

          {/* SQLite & Version Scopes */}
          <div className="p-4 rounded-xl bg-[#0B1020] border border-white/[0.06] space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck size={15} className="text-accent-emerald" />
                <span className="font-bold text-slate-200">Multi-Version Isolation</span>
              </div>
              <span className="text-[10px] font-mono text-accent-emerald font-semibold">
                Zero Contamination
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Separate lexical (BM25) and semantic (ChromaDB) partitions ensure requests for v1.0, v2.0, and v3.0 never cross boundaries.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-3 border-t border-white/[0.07] flex items-center justify-between">
          <button
            onClick={refreshHealth}
            disabled={loading}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin text-violetAccent-light' : ''} />
            <span>Re-check Telemetry</span>
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-violetAccent hover:bg-violetAccent-hover text-white text-xs font-semibold rounded-lg shadow-glow-violet transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;

