import React, { useState } from 'react';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import DashboardPage from './pages/DashboardPage';
import ChatInterface from './components/chat/ChatInterface';
import DocumentExplorer from './components/documents/DocumentExplorer';
import AnalyticsView from './components/analytics/AnalyticsView';

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <DashboardPage />}
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'documents' && <DocumentExplorer />}
        {activeTab === 'analytics' && <AnalyticsView />}
      </main>

      <Footer />
    </div>
  );
}

export default App;

