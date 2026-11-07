import React from 'react';
import { Database, Layers, Cpu, ShieldCheck } from 'lucide-react';

export function Footer() {
  return (
    <footer className="mt-auto border-t border-white/[0.08] bg-[#0B1020]/80 backdrop-blur-md text-slate-400 text-xs py-3.5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Brand */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="font-semibold text-white flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-blue"></span>
              <span>NexaDesk</span>
            </span>
            <span className="text-slate-500">·</span>
            <span className="text-slate-300 text-[11px]">
              Multi-Version RAG Customer Enquiry System
            </span>
          </div>

          {/* Architecture Badges */}
          <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-300">
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-[#141E33] border border-white/[0.08]">
              <Database size={10} className="text-accent-blue" />
              <span>ChromaDB</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-[#141E33] border border-white/[0.08]">
              <Layers size={10} className="text-accent-violet" />
              <span>BM25 Okapi</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-[#141E33] border border-white/[0.08]">
              <Cpu size={10} className="text-accent-emerald" />
              <span>Qwen 3.5 4B (Ollama)</span>
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
