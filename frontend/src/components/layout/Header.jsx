import React from 'react';
import {
  Menu,
  RefreshCw,
  Sparkles,
  BookOpen,
  BarChart3,
  LayoutDashboard,
  Settings,
  Shield,
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
      breadcrumb: 'Document Catalog',
      icon: BookOpen,
    },
    analytics: {
      title: 'Analytics',
      breadcrumb: 'Academic RAG Triad',
      icon: BarChart3,
    },
    settings: {
      title: 'Settings',
      breadcrumb: 'System & Model Configuration',
      icon: Settings,
    },
  };

  const currentMeta = tabMetadata[activeTab] || tabMetadata.dashboard;
  const TabIcon = currentMeta.icon;
  const versions = ['v1.0', 'v2.0', 'v3.0'];

  return (
    <header className="sticky top-0 z-30 bg-[#0B1020]/90 backdrop-blur-xl border-b border-white/[0.08] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-14 flex items-center justify-between gap-4">
          {/* Left: Mobile Trigger & Breadcrumb Navigation */}
          <div className="flex items-center space-x-3 min-w-0">
            <button
              onClick={onOpenMobileMenu}
              className="p-1.5 -ml-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] lg:hidden"
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>

            <div className="flex items-center space-x-2 text-xs min-w-0">
              <span className="text-slate-400 hidden sm:inline font-mono">NexaDesk</span>
              <ChevronRight size={12} className="text-slate-500 hidden sm:inline" />
              <div className="flex items-center space-x-1.5">
                <TabIcon size={14} className="text-accent-blue" />
                <h1 className="text-sm font-semibold text-white tracking-tight truncate">
                  {currentMeta.title}
                </h1>
              </div>
              <span className="text-slate-600 hidden md:inline">·</span>
              <span className="text-xs text-slate-300 hidden md:inline truncate">
                {currentMeta.breadcrumb}
              </span>
            </div>
          </div>

          {/* Right: Version Scope & Status Indicators */}
          <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
            {/* Global Product Version Selector */}
            <div className="flex items-center bg-[#141E33] p-0.5 rounded-xl border border-white/[0.08] text-xs">
              <span className="hidden lg:flex items-center space-x-1 px-2 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                <Shield size={11} className="text-accent-blue" />
                <span>Scope</span>
              </span>
              <div className="flex space-x-0.5">
                {versions.map((ver) => {
                  const isSelected = selectedVersion === ver;
                  return (
                    <button
                      key={ver}
                      onClick={() => setSelectedVersion(ver)}
                      className={`px-2.5 py-0.5 rounded-lg font-mono text-xs font-semibold transition-all ${
                        isSelected
                          ? 'bg-accent-blue text-white shadow-sm'
                          : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
                      }`}
                      title={`Context scope isolated to NexaDesk ${ver}`}
                    >
                      {ver}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Model & Backend Status */}
            <div
              onClick={onOpenSettings}
              className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-[#141E33] border border-white/[0.08] text-xs cursor-pointer hover:border-white/[0.15] transition-colors"
              title="Active LLM: Qwen 3.5 4B via Ollama"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse" />
              <span className="font-mono text-xs text-white">Qwen 3.5 4B</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-accent-blue/15 text-accent-blue font-mono font-semibold">
                Ollama
              </span>
            </div>

            {/* Refresh Diagnostics */}
            <button
              onClick={refreshHealth}
              disabled={loading}
              title="Refresh health telemetry"
              className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.04] border border-white/[0.08] bg-[#141E33] transition-colors"
            >
              <RefreshCw size={14} className={loading ? 'animate-spin text-accent-blue' : ''} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
