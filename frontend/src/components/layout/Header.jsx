import React from 'react';
import {
  Menu,
  RefreshCw,
  Cpu,
  Layers,
  Sparkles,
  Database,
  BarChart3,
  LayoutDashboard,
  Shield,
  Activity,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function Header({ activeTab, onOpenMobileMenu, onOpenSettings }) {
  const { selectedVersion, setSelectedVersion, refreshHealth, loading } = useSystem();

  const tabMetadata = {
    dashboard: {
      title: 'Overview',
      breadcrumb: 'Platform Operations',
      icon: LayoutDashboard,
    },
    chat: {
      title: 'AI Assistant',
      breadcrumb: 'Conversational Intelligence',
      icon: Sparkles,
    },
    documents: {
      title: 'Knowledge Base',
      breadcrumb: 'Document Catalog & Chunks',
      icon: Database,
    },
    analytics: {
      title: 'Evaluation & Analytics',
      breadcrumb: 'Academic RAG Triad Suite',
      icon: BarChart3,
    },
  };

  const currentMeta = tabMetadata[activeTab] || tabMetadata.dashboard;
  const TabIcon = currentMeta.icon;
  const versions = ['v1.0', 'v2.0', 'v3.0'];

  return (
    <header className="sticky top-0 z-30 bg-canvas-base/85 backdrop-blur-xl border-b border-white/[0.07] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-14 flex items-center justify-between gap-4">
          {/* Left: Mobile Trigger & Breadcrumb Navigation */}
          <div className="flex items-center space-x-3 min-w-0">
            <button
              onClick={onOpenMobileMenu}
              className="p-1.5 -ml-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] lg:hidden"
              aria-label="Open sidebar navigation"
            >
              <Menu size={18} />
            </button>

            <div className="flex items-center space-x-2 text-xs font-mono min-w-0">
              <span className="text-slate-500 hidden sm:inline">NexaDesk</span>
              <ChevronRight size={12} className="text-slate-600 hidden sm:inline" />
              <div className="flex items-center space-x-2">
                <TabIcon size={14} className="text-violetAccent-light" />
                <h1 className="text-sm font-bold text-white tracking-tight truncate">
                  {currentMeta.title}
                </h1>
              </div>
              <span className="text-slate-600 hidden md:inline">·</span>
              <span className="text-[11px] text-slate-400 font-sans hidden md:inline truncate">
                {currentMeta.breadcrumb}
              </span>
            </div>
          </div>

          {/* Right: Version Scope & Status Indicators */}
          <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
            {/* Global Product Version Selector */}
            <div className="flex items-center bg-canvas-card p-0.5 rounded-lg border border-white/[0.07] text-xs">
              <span className="hidden lg:flex items-center space-x-1 px-2 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                <Shield size={11} className="text-violetAccent-light" />
                <span>Scope</span>
              </span>
              <div className="flex space-x-0.5">
                {versions.map((ver) => {
                  const isSelected = selectedVersion === ver;
                  const activeStyle =
                    ver === 'v1.0'
                      ? 'bg-blue-600 text-white shadow-sm font-bold'
                      : ver === 'v2.0'
                      ? 'bg-violetAccent text-white shadow-glow-violet font-bold'
                      : 'bg-cyan-600 text-white shadow-sm font-bold';

                  return (
                    <button
                      key={ver}
                      onClick={() => setSelectedVersion(ver)}
                      className={`px-2 py-0.5 rounded-md font-mono text-[11px] font-semibold transition-all ${
                        isSelected
                          ? activeStyle
                          : 'text-slate-400 hover:text-white hover:bg-white/[0.05]'
                      }`}
                      title={`Strict context isolation bounded to NexaDesk ${ver}`}
                    >
                      {ver}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Model & Backend Telemetry Indicator */}
            <div
              onClick={onOpenSettings}
              className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-lg bg-canvas-card border border-white/[0.07] text-xs cursor-pointer hover:border-white/15 transition-colors"
              title="LLM Provider: Ollama · Model: Qwen 3.5 4B"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emeraldAccent opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emeraldAccent"></span>
              </span>
              <span className="font-mono text-[11px] text-slate-300">Qwen 3.5 4B</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-violetAccent/15 text-violetAccent-light border border-violetAccent/25 font-mono">
                Ollama
              </span>
            </div>

            {/* Refresh Diagnostics */}
            <button
              onClick={refreshHealth}
              disabled={loading}
              title="Refresh system diagnostics"
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] border border-white/[0.07] bg-canvas-card transition-colors"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin text-violetAccent-light' : ''} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
