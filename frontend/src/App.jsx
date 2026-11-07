import React, { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import DashboardPage from './pages/DashboardPage';
import ChatInterface from './components/chat/ChatInterface';
import DocumentExplorer from './components/documents/DocumentExplorer';
import AnalyticsView from './components/analytics/AnalyticsView';
import SettingsPage from './pages/SettingsPage';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#0B1020] text-slate-100 font-sans flex antialiased selection:bg-accent-blue/30 selection:text-white bg-ambient-glow">
      {/* Modern Compact Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        setMobileOpen={setMobileMenuOpen}
      />

      {/* Main Workspace Container */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-200 ease-in-out ${
          sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-56'
        }`}
      >
        {/* Compact Header */}
        <Header
          activeTab={activeTab}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          onOpenSettings={() => setActiveTab('settings')}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'dashboard' && <DashboardPage onNavigate={setActiveTab} />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'documents' && <DocumentExplorer />}
          {activeTab === 'analytics' && <AnalyticsView />}
          {activeTab === 'settings' && <SettingsPage />}
        </main>

        {/* Minimalist Bottom Footer */}
        <Footer />
      </div>
    </div>
  );
}

export default App;
