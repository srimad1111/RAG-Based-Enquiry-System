import React, { useState } from 'react';
import { Send, Bot, User, Sparkles, AlertCircle, HelpCircle } from 'lucide-react';
import { useSystem } from '../../context/SystemContext';

export function ChatInterface() {
  const { selectedVersion, health } = useSystem();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: `Hello! I am your NexaDesk Customer Support Assistant. I am currently configured with the ${selectedVersion} documentation catalog. How can I assist you today?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const sampleQueries = {
    'v1.0': [
      'What are the pricing tiers in v1.0?',
      'How does email ticket ingestion work?',
      'Is there an annual billing discount?',
    ],
    'v2.0': [
      'What new features were added in v2.0?',
      'How do round-robin automation rules work?',
      'Can I connect NexaDesk to Slack?',
    ],
    'v3.0': [
      'What is the NexaDesk AI Copilot?',
      'How does NexaFlow Workflow Studio replace legacy rules?',
      'What are the Enterprise SSO capabilities in v3.0?',
    ],
  };

  const handleSend = (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const scaffoldResponse = {
      id: Date.now() + 1,
      sender: 'assistant',
      text: `[Phase 1 System Notice]: You asked: "${query}" targeting documentation version [${selectedVersion}]. The full RAG retrieval pipeline (Hybrid BM25 + ChromaDB + Gemini LLM) will be activated in Phase 2. Your backend is connected and ready!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isSystemNotice: true,
    };

    setMessages((prev) => [...prev, userMessage, scaffoldResponse]);
    setQuery('');
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[650px] overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center">
            <Bot size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-800">NexaDesk Support Assistant</h3>
            <p className="text-xs text-slate-500">
              Active Context: <span className="font-mono font-semibold text-indigo-600">{selectedVersion}</span> Documentation
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>FastAPI Connected</span>
        </div>
      </div>

      {/* Message history */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-2.5 ${msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs flex-shrink-0 ${
                msg.sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-700'
              }`}
            >
              {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div
              className={`max-w-[75%] rounded-xl px-4 py-2.5 text-xs ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white'
                  : msg.isSystemNotice
                  ? 'bg-indigo-50 border border-indigo-200 text-indigo-900'
                  : 'bg-slate-100 text-slate-800'
              }`}
            >
              <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
              <span className={`block text-[10px] mt-1 ${msg.sender === 'user' ? 'text-indigo-200 text-right' : 'text-slate-400'}`}>
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Suggested Inquiries */}
      <div className="px-4 py-2 bg-slate-50/70 border-t border-slate-100">
        <div className="flex items-center space-x-2 mb-1.5 text-[11px] text-slate-500">
          <HelpCircle size={12} className="text-indigo-600" />
          <span>Suggested queries for NexaDesk {selectedVersion}:</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {(sampleQueries[selectedVersion] || []).map((sample) => (
            <button
              key={sample}
              onClick={() => setQuery(sample)}
              className="text-[11px] px-2.5 py-1 bg-white hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 rounded-md text-slate-600 transition-colors"
            >
              {sample}
            </button>
          ))}
        </div>
      </div>

      {/* Input box */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-200 bg-white flex items-center space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Ask an inquiry grounded in NexaDesk ${selectedVersion} docs...`}
          className="flex-1 text-xs border border-slate-300 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
        <button
          type="submit"
          disabled={!query.trim()}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-sm"
        >
          <span>Send</span>
          <Send size={13} />
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;

