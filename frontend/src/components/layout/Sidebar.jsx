import React from 'react';
import {
  LayoutDashboard,
  Sparkles,
  Database,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Cpu,
  Layers,
  X,
  ShieldCheck,
  Activity,
  Circle,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed, mobileOpen, setMobileOpen, onOpenSettings }) {
  const { health, selectedVersion } = useSystem();

  const navItems = [
    {
      id: 'dashboard',
      label: 'Overview',
      sublabel: 'Command Center',
      icon: LayoutDashboard,
      badge: 'Live',
    },
    {
      id: 'chat',
      label: 'AI Assistant',
      sublabel: 'Customer Intelligence',
      icon: Sparkles,
      badge: 'Qwen 4B',
    },
    {
      id: 'documents',
      label: 'Knowledge Base',
      sublabel: 'Document Catalog',
      icon: Database,
      badge: `${health?.stats?.total_documents ?? 18}`,
    },
    {
      id: 'analytics',
      label: 'Evaluation & Analytics',
      sublabel: 'Academic RAG Triad',
      icon: BarChart3,
      badge: 'Phase 7',
    },
  ];

  const handleNavClick = (tabId) => {
    setActiveTab(tabId);
    if (mobileOpen) setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-canvas-void/80 backdrop-blur-md z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Root */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-canvas-sidebar border-r border-white/[0.07] text-slate-300 transition-all duration-300 ease-in-out select-none ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${collapsed ? 'w-20' : 'w-64'}`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-white/[0.07] bg-canvas-void/40">
          <div className="flex items-center space-x-3 overflow-hidden">
            {/* Linear-Style NexaDesk Logo Emblem */}
            <div className="relative flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-tr from-violetAccent to-blueAccent p-[1px] shadow-glow-violet">
              <div className="w-full h-full bg-canvas-card rounded-[7px] flex items-center justify-center">
                <Cpu className="w-4 h-4 text-violetAccent-light" />
              </div>
            </div>

            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <div className="flex items-center space-x-1.5">
                  <span className="text-sm font-bold tracking-tight text-white">
                    NexaDesk
                  </span>
                  <span className="text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.2 rounded bg-violetAccent/15 text-violetAccent-light border border-violetAccent/30">
                    AI SAAS
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono truncate">
                  Enterprise RAG Engine
                </span>
              </div>
            )}
          </div>

          {/* Close trigger for Mobile */}
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] lg:hidden"
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 py-4 px-2.5 space-y-1 overflow-y-auto">
          {!collapsed && (
            <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              Platform Navigation
            </div>
          )}

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                title={collapsed ? `${item.label} · ${item.sublabel}` : undefined}
                className={`group relative w-full flex items-center rounded-xl transition-all duration-150 text-left ${
                  collapsed ? 'justify-center p-3' : 'px-3 py-2.5'
                } ${
                  isActive
                    ? 'bg-violetAccent/15 text-white shadow-sm border border-violetAccent/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                {/* Active Indicator Bar */}
                {isActive && (
                  <div className="absolute left-0 top-2 bottom-2 w-1 bg-violetAccent rounded-r shadow-glow-violet" />
                )}

                <div className={`flex items-center justify-center ${collapsed ? '' : 'mr-3'}`}>
                  <Icon
                    size={18}
                    className={`transition-colors ${
                      isActive
                        ? 'text-violetAccent-light drop-shadow-[0_0_8px_rgba(139,92,246,0.5)]'
                        : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  />
                </div>

                {!collapsed && (
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-semibold truncate ${isActive ? 'text-white' : 'text-slate-300'}`}>
                        {item.label}
                      </span>
                      {item.badge && (
                        <span
                          className={`text-[9px] font-mono px-1.5 py-0.5 rounded-md ${
                            isActive
                              ? 'bg-violetAccent/20 text-violetAccent-light border border-violetAccent/30'
                              : 'bg-white/[0.05] text-slate-400 border border-white/[0.05]'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-500 truncate block">
                      {item.sublabel}
                    </span>
                  </div>
                )}
              </button>
            );
          })}

          {/* Settings Nav Item (Triggers Settings Modal) */}
          <button
            onClick={onOpenSettings}
            title={collapsed ? 'System Engine Settings' : undefined}
            className={`group w-full flex items-center rounded-xl transition-all duration-150 text-left mt-2 ${
              collapsed ? 'justify-center p-3' : 'px-3 py-2.5'
            } text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]`}
          >
            <div className={`flex items-center justify-center ${collapsed ? '' : 'mr-3'}`}>
              <Settings size={18} className="text-slate-400 group-hover:text-slate-200 transition-colors" />
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <span className="text-xs font-semibold text-slate-300 block truncate">
                  Settings & Telemetry
                </span>
                <span className="text-[10px] text-slate-500 truncate block">
                  Ollama & ChromaDB
                </span>
              </div>
            )}
          </button>
        </div>

        {/* User / Admin Profile Area & Collapse Toggle */}
        <div className="p-3 border-t border-white/[0.07] bg-canvas-void/50 space-y-2">
          {!collapsed ? (
            <div className="rounded-xl border border-white/[0.06] bg-canvas-card/60 p-2.5 flex items-center justify-between">
              <div className="flex items-center space-x-2.5 min-w-0">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-violetAccent to-blueAccent flex items-center justify-center text-[11px] font-bold text-white flex-shrink-0 shadow-sm">
                  AD
                </div>
                <div className="min-w-0">
                  <div className="flex items-center space-x-1.5">
                    <span className="text-xs font-semibold text-white truncate">Admin User</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-emeraldAccent animate-pulse" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 truncate block">
                    NexaDesk {selectedVersion}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-1">
                <button
                  onClick={onOpenSettings}
                  className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
                  title="Configure Engine"
                >
                  <Settings size={14} />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex justify-center py-1">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-violetAccent to-blueAccent flex items-center justify-center text-[10px] font-bold text-white shadow-sm" title={`Admin User · NexaDesk ${selectedVersion}`}>
                AD
              </div>
            </div>
          )}

          {/* Desktop Collapse Trigger */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex items-center justify-center w-full py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] transition-colors text-xs font-medium"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight size={15} /> : (
              <div className="flex items-center space-x-1 text-[11px] text-slate-400">
                <ChevronLeft size={13} />
                <span>Collapse</span>
              </div>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
