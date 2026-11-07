import React from 'react';
import { Cpu, ShieldCheck, Database, Layers, Sparkles } from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function Footer() {
  const { systemInfo } = useSystem();

  return (
    <footer className="mt-auto border-t border-white/[0.06] bg-canvas-base/60 backdrop-blur-md text-slate-400 text-xs py-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-3">
          {/* Brand & Capstone note */}
          <div className="flex flex-wrap items-center gap-2 text-slate-400">
            <span className="font-bold text-white tracking-tight flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-violetAccent"></span>
              <span>NexaDesk</span>
            </span>
            <span className="text-slate-600">·</span>
            <span className="text-[11px] text-slate-400">
              Intelligence Behind Every Customer Interaction
            </span>
            <span className="text-slate-600">·</span>
            <span className="text-[10px] font-mono text-slate-500">Project 32</span>
          </div>

          {/* Actual Architecture Badges */}
          <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono">
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-white/[0.04] text-slate-300 border border-white/[0.06]">
              <Database size={10} className="text-blueAccent" />
              <span>ChromaDB (384-d)</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-white/[0.04] text-slate-300 border border-white/[0.06]">
              <Layers size={10} className="text-violetAccent-light" />
              <span>BM25 Okapi</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-white/[0.04] text-slate-300 border border-white/[0.06]">
              <Cpu size={10} className="text-emeraldAccent" />
              <span>Ollama (Qwen 3.5 4B)</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-white/[0.04] text-slate-300 border border-white/[0.06]">
              <ShieldCheck size={10} className="text-amberAccent" />
              <span>Version Isolation</span>
            </span>
          </div>

          {/* Right Status */}
          <div className="text-[10px] font-mono text-slate-500">
            <span>Production v1.0.0</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
