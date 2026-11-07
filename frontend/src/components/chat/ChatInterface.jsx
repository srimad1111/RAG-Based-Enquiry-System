import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  Layers,
  Database,
  RefreshCw,
  HelpCircle,
  FileText,
  Tag,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Split,
  Search,
  Sliders,
  Terminal,
  Activity,
  Zap,
  Info,
  BookOpen,
  MessageSquare,
  Key,
  Trash2,
  ExternalLink,
  ChevronDown,
  X
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';
import chatService from '../../services/chatService';
import ragService from '../../services/ragService';
import { Badge } from '../common/Badge';

export function ChatInterface() {
  const { selectedVersion, setSelectedVersion } = useSystem();

  // Navigation tab: 'chat' (Phase 5) or 'inspector' (Phase 4)
  const [activeTab, setActiveTab] = useState('chat');

  // Conversation State
  const [conversationId, setConversationId] = useState(() => `conv_${Date.now()}`);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: `Hello! I am your official NexaDesk AI Support Assistant grounded in the **${selectedVersion}** documentation. How can I assist you with ${selectedVersion} features, pricing, or configuration today?`,
      citations: [],
      abstained: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [sending, setSending] = useState(false);
  const [chatConfig, setChatConfig] = useState(null);

  // Citation Inspector Modal
  const [activeCitation, setActiveCitation] = useState(null);

  // API Key Settings Modal
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [customApiKey, setCustomApiKey] = useState(() => localStorage.getItem('nexadesk_gemini_api_key') || '');

  // Retrieval Settings (for console tab)
  const [retrievalMode, setRetrievalMode] = useState('hybrid');
  const [enableRewriting, setEnableRewriting] = useState(true);
  const [topK, setTopK] = useState(4);
  const [ragStatus, setRagStatus] = useState(null);
  const [syncingIndex, setSyncingIndex] = useState(false);
  const [consoleQuery, setConsoleQuery] = useState('');
  const [consoleData, setConsoleData] = useState(null);
  const [consoleView, setConsoleView] = useState('results');
  const [methodsComparison, setMethodsComparison] = useState(null);
  const [loadingConsole, setLoadingConsole] = useState(false);

  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  // Load chat & RAG config
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const [cfg, status] = await Promise.all([
          chatService.getConfig(),
          ragService.getStatus()
        ]);
        setChatConfig(cfg);
        setRagStatus(status);
      } catch (err) {
        console.error('Failed to load chat configuration:', err);
      }
    };
    loadConfig();
  }, []);

  // Update welcome message on version change
  useEffect(() => {
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: 'assistant',
        content: `*Switched context scope to **NexaDesk ${selectedVersion}**.* Answers will now be strictly grounded in ${selectedVersion} documentation.`,
        citations: [],
        abstained: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
    ]);
  }, [selectedVersion]);

  // Suggested test queries tailored per version
  const sampleInquiries = {
    'v1.0': [
      "Why can't I schedule my reports like before?",
      "What are the pricing tiers and user limits?",
      "How does email ticket ingestion work?",
      "What user roles are supported in v1.0?"
    ],
    'v2.0': [
      "Why can't I schedule my reports like before?",
      "How do round robin ticket assignment rules work?",
      "Can I connect NexaDesk to Slack channels?",
      "What is the annual billing discount?"
    ],
    'v3.0': [
      "How do automated report exports and AI summaries work?",
      "What is the NexaDesk AI Copilot and NexaFlow Studio?",
      "What are the Enterprise SAML SSO capabilities?",
      "What are the Growth and Scale tier quotas?"
    ]
  };

  // Submit enquiry to Phase 5 RAG pipeline
  const handleSendEnquiry = async (textToSend = inputQuery) => {
    const q = textToSend || inputQuery;
    if (!q.trim() || sending) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery('');
    setSending(true);

    try {
      const res = await chatService.submitEnquiry({
        question: q,
        product_version: selectedVersion,
        product_name: 'NexaDesk',
        conversation_id: conversationId,
        retrieval_mode: retrievalMode,
        top_k: topK,
        enable_rewriting: enableRewriting,
        temperature: 0.1,
        api_key: customApiKey || undefined
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.answer,
        citations: res.citations || [],
        abstained: res.abstained || false,
        rewritten_query: res.rewritten_query,
        latency_ms: res.latency_ms,
        model_used: res.model_used,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Enquiry failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: `⚠️ Error communicating with support backend: ${err.message || 'Server error'}. Please check if the FastAPI backend is running.`,
          citations: [],
          abstained: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      setSending(false);
    }
  };

  // Save custom API key
  const handleSaveApiKey = () => {
    setCustomApiKey(apiKeyInput.trim());
    if (apiKeyInput.trim()) {
      localStorage.setItem('nexadesk_gemini_api_key', apiKeyInput.trim());
    } else {
      localStorage.removeItem('nexadesk_gemini_api_key');
    }
    setShowKeyModal(false);
  };

  // Reset conversation
  const handleResetChat = () => {
    const newId = `conv_${Date.now()}`;
    setConversationId(newId);
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: `Conversation restarted. I am your NexaDesk Support Assistant for **${selectedVersion}**. How can I assist you?`,
        citations: [],
        abstained: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
    ]);
  };

  // Console retrieval handlers (Phase 4 view)
  const handleRunConsole = async (q = consoleQuery) => {
    if (!q.trim()) return;
    setLoadingConsole(true);
    setConsoleView('results');
    try {
      const res = await ragService.retrieveHybrid({
        customer_question: q,
        product_version: selectedVersion,
        enable_query_rewriting: enableRewriting,
        retrieval_mode: retrievalMode,
        top_k: topK
      });
      setConsoleData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingConsole(false);
    }
  };

  const handleRunCompareMethods = async (q = consoleQuery) => {
    if (!q.trim()) return;
    setLoadingConsole(true);
    setConsoleView('compare_methods');
    try {
      const res = await ragService.compareRetrievalMethods({
        customer_question: q,
        product_version: selectedVersion,
        top_k: 3
      });
      setMethodsComparison(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingConsole(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Bar: Mode Selector & Scope */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              activeTab === 'chat'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <MessageSquare size={14} />
            <span>AI Customer Assistant (Phase 5)</span>
          </button>

          <button
            onClick={() => setActiveTab('inspector')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
              activeTab === 'inspector'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Terminal size={14} />
            <span>Hybrid Retrieval Console (Phase 4)</span>
          </button>
        </div>

        {/* Scope and Controls */}
        <div className="flex items-center space-x-3">
          {/* Target Version Selector */}
          <div className="flex items-center bg-slate-50 border border-slate-200 p-1 rounded-lg">
            <span className="text-[11px] font-semibold text-slate-500 px-2">Doc Scope:</span>
            {['v1.0', 'v2.0', 'v3.0'].map((ver) => (
              <button
                key={ver}
                onClick={() => setSelectedVersion(ver)}
                className={`px-2.5 py-1 text-xs font-bold rounded-md transition-all ${
                  selectedVersion === ver
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {ver}
              </button>
            ))}
          </div>

          {/* API Key Modal Button */}
          <button
            onClick={() => {
              setApiKeyInput(customApiKey);
              setShowKeyModal(true);
            }}
            className="flex items-center space-x-1 px-2.5 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg shadow-xs"
            title="Configure personal Gemini API Key"
          >
            <Key size={13} className={customApiKey ? 'text-emerald-600' : 'text-slate-400'} />
            <span className="hidden md:inline">{customApiKey ? 'API Key Set' : 'Gemini Key'}</span>
          </button>

          {/* Reset Chat Button */}
          {activeTab === 'chat' && (
            <button
              onClick={handleResetChat}
              className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
              title="Reset conversation thread"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: Conversational Customer Enquiry Chatbot (Phase 5)
          ========================================================================= */}
      {activeTab === 'chat' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[700px] overflow-hidden">
          {/* Header */}
          <div className="p-3.5 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs">
                <Bot size={18} />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
                  <span>NexaDesk Customer Support Assistant</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
                    Grounded RAG
                  </span>
                </h3>
                <p className="text-xs text-slate-500">
                  Strictly grounded in <span className="font-bold text-indigo-600 font-mono">NexaDesk {selectedVersion}</span> documentation with source citations.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3 text-xs text-slate-500">
              <span className="hidden sm:inline font-mono text-[11px]">
                Engine: <span className="font-semibold text-slate-700">{chatConfig?.llm_model || 'gemini-1.5-flash'}</span>
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/30">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-2.5 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}
              >
                {/* Avatar */}
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs flex-shrink-0 shadow-xs ${
                    msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-indigo-600'
                  }`}
                >
                  {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                </div>

                {/* Message Bubble */}
                <div
                  className={`max-w-[80%] rounded-xl p-3.5 text-xs shadow-xs space-y-2.5 ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border border-slate-200 text-slate-800'
                  }`}
                >
                  {/* Rewritten Query Sub-pill (if available) */}
                  {msg.rewritten_query && msg.rewritten_query !== msg.content && (
                    <div className="text-[10px] text-slate-500 bg-slate-50 px-2 py-1 rounded border border-slate-100 flex items-center space-x-1.5">
                      <Terminal size={11} className="text-indigo-500" />
                      <span>Interpreted technical query: <span className="font-semibold text-slate-700">{msg.rewritten_query}</span></span>
                    </div>
                  )}

                  {/* Main Answer Content */}
                  <div className="leading-relaxed whitespace-pre-wrap font-sans text-xs">
                    {msg.content}
                  </div>

                  {/* Abstention Warning & Escalation Offer */}
                  {msg.abstained && (
                    <div className="mt-2 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2">
                      <AlertTriangle size={15} className="text-amber-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-[11px]">Strict Grounding Notice:</p>
                        <p className="text-[11px] text-amber-800 mt-0.5">
                          Information could not be verified from available {selectedVersion} documentation. Hallucination prevention active.
                        </p>
                        <button
                          onClick={() => alert(`Escalating inquiry to NexaDesk Human Support Tier (Ticket created under session ${conversationId})`)}
                          className="mt-1.5 px-2.5 py-1 text-[10px] font-bold bg-amber-600 hover:bg-amber-700 text-white rounded transition-colors"
                        >
                          Escalate to Human Support Agent
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Verifiable Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 border-t border-slate-100 space-y-1.5">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block flex items-center space-x-1">
                        <BookOpen size={11} className="text-indigo-600" />
                        <span>Verifiable Sources ({msg.citations.length}):</span>
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.citations.map((cite) => (
                          <button
                            key={cite.citation_id}
                            onClick={() => setActiveCitation(cite)}
                            className="text-[10px] font-medium px-2 py-1 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 border border-slate-200 rounded-md text-slate-700 transition-colors flex items-center space-x-1 group"
                          >
                            <FileText size={10} className="text-slate-400 group-hover:text-indigo-500" />
                            <span className="font-semibold truncate max-w-[140px]">{cite.document_name}</span>
                            <span className="text-slate-400">·</span>
                            <span>p.{cite.page_number}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Message Timestamp & Latency */}
                  <div className="flex items-center justify-between text-[10px] pt-1">
                    <span className={msg.role === 'user' ? 'text-indigo-200' : 'text-slate-400'}>
                      {msg.timestamp}
                    </span>
                    {msg.latency_ms && (
                      <span className="font-mono text-slate-400">
                        {msg.latency_ms} ms · {msg.model_used}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {sending && (
              <div className="flex items-center space-x-2 text-xs text-slate-500 py-2">
                <div className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center animate-pulse">
                  <Bot size={13} />
                </div>
                <span>NexaDesk AI is analyzing {selectedVersion} documentation and synthesizing response...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Inquiries for Active Version */}
          <div className="px-4 py-2 bg-slate-50 border-t border-slate-100">
            <div className="flex items-center space-x-1.5 mb-1.5 text-[11px] text-slate-500">
              <HelpCircle size={12} className="text-indigo-600" />
              <span>Suggested customer questions for NexaDesk {selectedVersion}:</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(sampleInquiries[selectedVersion] || []).map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendEnquiry(sample)}
                  disabled={sending}
                  className="text-[11px] px-2.5 py-1 bg-white hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 rounded-md text-slate-700 transition-colors disabled:opacity-50"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form onSubmit={(e) => { e.preventDefault(); handleSendEnquiry(); }} className="p-3 border-t border-slate-200 bg-white flex items-center space-x-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder={`Ask any customer enquiry about NexaDesk ${selectedVersion}...`}
              disabled={sending}
              className="flex-1 text-xs border border-slate-300 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white shadow-xs"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || sending}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center space-x-1.5 text-xs font-semibold shadow-xs"
            >
              <span>Send</span>
              <Send size={13} />
            </button>
          </form>
        </div>
      )}

      {/* =========================================================================
          TAB 2: Hybrid Retrieval & RRF Console (Phase 4 View)
          ========================================================================= */}
      {activeTab === 'inspector' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Terminal size={16} className="text-indigo-600" />
                <span>RAG Retrieval Diagnostics & Reciprocal Rank Fusion</span>
              </h3>
              <p className="text-xs text-slate-500">
                Inspect raw query rewriting, Dense vs BM25 ranks, and 3-way retrieval strategy comparisons.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-indigo-100 text-indigo-800">
                Scope: {selectedVersion}
              </span>
            </div>
          </div>

          {/* Console Input Bar */}
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={consoleQuery}
              onChange={(e) => setConsoleQuery(e.target.value)}
              placeholder="Enter customer question to inspect retrieval (e.g. 'Why can't I schedule my reports like before?')..."
              className="flex-1 text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white"
            />
            <button
              onClick={() => handleRunConsole()}
              disabled={!consoleQuery.trim() || loadingConsole}
              className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
            >
              Inspect Hybrid
            </button>
            <button
              onClick={() => handleRunCompareMethods()}
              disabled={!consoleQuery.trim() || loadingConsole}
              className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold"
            >
              Compare 3 Methods
            </button>
          </div>

          {/* Output Display */}
          {loadingConsole && (
            <div className="py-12 text-center text-xs text-slate-500">
              <RefreshCw size={24} className="animate-spin text-indigo-600 mx-auto mb-2" />
              Running retrieval evaluation...
            </div>
          )}

          {!loadingConsole && consoleView === 'results' && consoleData && (
            <div className="space-y-3">
              <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-200 text-xs space-y-1">
                <p><strong>Rewritten Query:</strong> "{consoleData.rewritten_query}"</p>
                <p><strong>Detected Intent:</strong> {consoleData.diagnostics?.intent_detected}</p>
                <p><strong>Keywords:</strong> {consoleData.search_keywords?.join(', ')}</p>
              </div>

              <div className="space-y-2">
                {consoleData.results?.map((r, i) => (
                  <div key={i} className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between font-semibold">
                      <span>{r.document_name} (§ {r.section_title})</span>
                      <span className="font-mono text-indigo-700">RRF: {(r.rrf_score * 100).toFixed(1)}%</span>
                    </div>
                    <p className="text-slate-600 text-[11px] font-mono whitespace-pre-wrap">{r.text_content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loadingConsole && consoleView === 'compare_methods' && methodsComparison && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-2">
                <span className="font-bold text-slate-800 uppercase block">1. Raw Dense</span>
                {methodsComparison.raw_dense_results?.map((r, i) => (
                  <div key={i} className="bg-white p-2 rounded border border-slate-200">
                    <p className="font-semibold truncate">{r.document_name}</p>
                    <p className="text-[10px] text-slate-500">Sim: {r.dense_score?.toFixed(3)}</p>
                  </div>
                ))}
              </div>
              <div className="bg-blue-50/50 p-3 rounded-lg border border-blue-200 space-y-2">
                <span className="font-bold text-blue-900 uppercase block">2. Rewritten Dense</span>
                {methodsComparison.rewritten_dense_results?.map((r, i) => (
                  <div key={i} className="bg-white p-2 rounded border border-blue-200">
                    <p className="font-semibold truncate">{r.document_name}</p>
                    <p className="text-[10px] text-blue-600">Sim: {r.dense_score?.toFixed(3)}</p>
                  </div>
                ))}
              </div>
              <div className="bg-indigo-50/50 p-3 rounded-lg border border-indigo-200 space-y-2">
                <span className="font-bold text-indigo-900 uppercase block">3. Rewritten Hybrid (RRF)</span>
                {methodsComparison.rewritten_hybrid_results?.map((r, i) => (
                  <div key={i} className="bg-white p-2 rounded border border-indigo-200">
                    <p className="font-semibold truncate">{r.document_name}</p>
                    <p className="text-[10px] text-indigo-700 font-bold">RRF: {(r.rrf_score * 100).toFixed(1)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          CITATION INSPECTOR MODAL
          ========================================================================= */}
      {activeCitation && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden space-y-3 p-5">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <BookOpen size={16} className="text-indigo-600" />
                <h4 className="text-sm font-bold text-slate-900">Verifiable Source Citation</h4>
              </div>
              <button onClick={() => setActiveCitation(null)} className="text-slate-400 hover:text-slate-700">
                <X size={18} />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px]">
                <div><span className="text-slate-500">Document:</span> <span className="font-semibold text-slate-800">{activeCitation.document_name}</span></div>
                <div><span className="text-slate-500">Page:</span> <span className="font-semibold text-slate-800">{activeCitation.page_number}</span></div>
                <div><span className="text-slate-500">Section:</span> <span className="font-semibold text-slate-800">{activeCitation.section_title}</span></div>
                <div><span className="text-slate-500">Format:</span> <span className="font-semibold uppercase text-indigo-600">{activeCitation.document_type}</span></div>
              </div>

              <div>
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                  Retrieved Documentation Content:
                </span>
                <p className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 font-mono leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {activeCitation.snippet}
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setActiveCitation(null)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          GEMINI API KEY MODAL
          ========================================================================= */}
      {showKeyModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full border border-slate-200 p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <Key size={16} className="text-indigo-600" />
                <h4 className="text-sm font-bold text-slate-900">Configure Gemini API Key</h4>
              </div>
              <button onClick={() => setShowKeyModal(false)} className="text-slate-400 hover:text-slate-700">
                <X size={18} />
              </button>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              You can supply your Google Gemini API key to run live response generation with <strong>gemini-1.5-flash</strong>.
              If left blank, the assistant automatically uses our deterministic, grounded fallback synthesis engine.
            </p>

            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full text-xs font-mono border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-200">
              <button
                onClick={() => setShowKeyModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveApiKey}
                className="px-4 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg"
              >
                Save Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
