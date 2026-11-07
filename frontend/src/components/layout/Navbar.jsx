import React from 'react';
import { Bot, RefreshCw, Server, CheckCircle2, XCircle } from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function Navbar({ activeTab, setActiveTab }) {
  const { health, systemInfo, loading, selectedVersion, setSelectedVersion, refreshHealth } = useSystem();
  const isHealthy = health?.status === 'healthy';

  const versions = systemInfo?.supported_product_versions || ['v1.0', 'v2.0', 'v3.0'];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-white shadow-md">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">NexaDesk Support AI</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-100 text-indigo-700">
                  Capstone P32
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                RAG Customer Enquiry System over Multi-Version Documentation
              </p>
            </div>
          </div>

          {/* Version Selector & Status Actions */}
          <div className="flex items-center space-x-4">
            {/* Version Toggle */}
            <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
              <span className="text-xs font-medium text-slate-500 px-2 hidden md:inline">Doc Version:</span>
              {versions.map((ver) => (
                <button
                  key={ver}
                  onClick={() => setSelectedVersion(ver)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                    selectedVersion === ver
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {ver}
                </button>
              ))}
            </div>

            {/* Backend Health Status Badge */}
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-50 border border-slate-200">
                <span className="relative flex h-2 w-2">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isHealthy ? 'bg-emerald-400' : 'bg-rose-400'
                  }`}></span>
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${
                    isHealthy ? 'bg-emerald-500' : 'bg-rose-500'
                  }`}></span>
                </span>
                <span className="text-slate-700 font-mono text-[11px]">
                  {loading ? 'Checking...' : isHealthy ? 'API Online' : 'API Offline'}
                </span>
              </div>

              {/* Refresh Button */}
              <button
                onClick={refreshHealth}
                disabled={loading}
                title="Refresh Health Check"
                className="p-1.5 text-slate-500 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-6 -mb-px pt-1 text-sm font-medium">
          {[
            { id: 'dashboard', label: 'System Dashboard' },
            { id: 'chat', label: 'Inquiry Chat Assistant' },
            { id: 'documents', label: 'Document Catalog' },
            { id: 'analytics', label: 'Evaluation & Analytics' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 px-1 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-indigo-600 text-indigo-600 font-semibold'
                  : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}

export default Navbar;

