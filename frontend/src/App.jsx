import React, { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import DashboardPage from './pages/DashboardPage';
import ChatInterface from './components/chat/ChatInterface';
import DocumentExplorer from './components/documents/DocumentExplorer';
import AnalyticsView from './components/analytics/AnalyticsView';
import SettingsModal from './components/common/SettingsModal';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-canvas-base text-slate-100 font-sans flex antialiased selection:bg-violetAccent/30 selection:text-white">
      {/* Modern Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        setMobileOpen={setMobileMenuOpen}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      {/* Main Content Workspace Container */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out ${
          sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'
        }`}
      >
        {/* Compact Top Header */}
        <Header
          activeTab={activeTab}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          onOpenSettings={() => setSettingsOpen(true)}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {activeTab === 'dashboard' && <DashboardPage onNavigate={setActiveTab} />}
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'documents' && <DocumentExplorer />}
          {activeTab === 'analytics' && <AnalyticsView />}
        </main>

        {/* Bottom Technology & Capstone Footer */}
        <Footer />
      </div>

      {/* System Engine Settings Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  );
}

export default App;
