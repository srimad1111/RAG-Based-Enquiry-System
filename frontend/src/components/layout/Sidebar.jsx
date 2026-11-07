import React from 'react';
import {
  LayoutDashboard,
  Sparkles,
  BookOpen,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Cpu,
  X,
  User,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed, mobileOpen, setMobileOpen }) {
  const { health } = useSystem();

  const navItems = [
    {
      id: 'dashboard',
      label: 'Overview',
      icon: LayoutDashboard,
    },
    {
      id: 'chat',
      label: 'AI Assistant',
      icon: Sparkles,
    },
    {
      id: 'documents',
      label: 'Knowledge Base',
      icon: BookOpen,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
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
          className="fixed inset-0 bg-[#070A14]/80 backdrop-blur-md z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Root */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-[#0E1526] border-r border-white/[0.08] text-slate-300 transition-all duration-200 ease-in-out select-none ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${collapsed ? 'w-16' : 'w-56'}`}
      >
        {/* Brand Header */}
        <div className="h-14 px-3.5 flex items-center justify-between border-b border-white/[0.08]">
          <div className="flex items-center space-x-2.5 overflow-hidden">
            {/* Minimalist Logo Emblem */}
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-accent-blue to-accent-violet p-[1px] flex-shrink-0 shadow-glow-blue">
              <div className="w-full h-full bg-[#141E33] rounded-[7px] flex items-center justify-center">
                <Cpu className="w-3.5 h-3.5 text-accent-blue" />
              </div>
            </div>

            {!collapsed && (
              <div className="flex items-center space-x-1.5 min-w-0">
                <span className="text-sm font-bold tracking-tight text-white truncate">
                  NexaDesk
                </span>
                <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-accent-blue/15 text-accent-blue border border-accent-blue/20">
                  AI
                </span>
              </div>
            )}
          </div>

          {/* Close trigger for Mobile */}
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] lg:hidden"
            aria-label="Close navigation"
          >
            <X size={16} />
          </button>
        </div>

        {/* Clean Navigation Items - No Subtitles, No Badges */}
        <div className="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                title={collapsed ? item.label : undefined}
                className={`relative w-full flex items-center rounded-xl transition-colors duration-150 text-left ${
                  collapsed ? 'justify-center p-2.5' : 'px-3 py-2'
                } ${
                  isActive
                    ? 'bg-accent-blue/15 text-white font-medium border border-accent-blue/25'
                    : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
                }`}
              >
                {/* Active Indicator Bar */}
                {isActive && (
                  <div className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-accent-blue rounded-r" />
                )}

                <div className={`flex items-center justify-center ${collapsed ? '' : 'mr-2.5'}`}>
                  <Icon
                    size={16}
                    className={`transition-colors ${
                      isActive ? 'text-accent-blue' : 'text-slate-400'
                    }`}
                  />
                </div>

                {!collapsed && (
                  <span className={`text-xs truncate font-medium ${isActive ? 'text-white' : 'text-slate-300'}`}>
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Compact Admin Profile & Collapse Trigger at Bottom */}
        <div className="p-2 border-t border-white/[0.08] space-y-1">
          {/* Admin Profile */}
          <div
            className={`flex items-center rounded-xl p-2 bg-[#141E33] border border-white/[0.08] ${
              collapsed ? 'justify-center' : 'justify-between'
            }`}
          >
            <div className="flex items-center space-x-2 min-w-0">
              <div className="w-6 h-6 rounded-full bg-accent-violet/20 border border-accent-violet/30 flex items-center justify-center text-accent-violet flex-shrink-0">
                <User size={12} />
              </div>
              {!collapsed && (
                <div className="min-w-0">
                  <span className="text-xs font-semibold text-white truncate block">
                    Admin
                  </span>
                  <span className="text-[10px] text-slate-400 truncate block font-mono">
                    NexaDesk Enterprise
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Collapse/Expand Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex w-full items-center justify-center p-1.5 text-slate-400 hover:text-white hover:bg-white/[0.04] rounded-lg text-xs transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            {!collapsed && <span className="ml-1 text-[11px]">Collapse</span>}
          </button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
