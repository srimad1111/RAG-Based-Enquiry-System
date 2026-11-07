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
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Terminal,
  Activity,
  Zap,
  BookOpen,
  MessageSquare,
  Key,
  Trash2,
  X,
  Copy,
  Check,
  ShieldAlert,
  Settings,
  ChevronRight,
  Info,
  Shield,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';
import chatService from '../../services/chatService';
import ragService from '../../services/ragService';
import MarkdownRenderer from '../common/MarkdownRenderer';

export function ChatInterface() {
  const { selectedVersion, setSelectedVersion } = useSystem();

  // Tab: 'chat' (Enterprise AI Assistant) or 'inspector' (Retrieval Console)
  const [activeTab, setActiveTab] = useState('chat');
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  const handleCopyAnswer = (messageId, text) => {
    try {
      navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => {
        setCopiedMessageId((prev) => (prev === messageId ? null : prev));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  // Conversation Thread State
  const [conversationId, setConversationId] = useState(() => `conv_${Date.now()}`);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: `Welcome to NexaDesk Intelligence. I am your customer support AI grounded strictly in **NexaDesk ${selectedVersion}** documentation.\n\nAsk any question regarding configurations, automated reports, SLA policies, or ticket workflows for **${selectedVersion}**.`,
      citations: [],
      abstained: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [sending, setSending] = useState(false);
  const [generationStep, setGenerationStep] = useState(1);
  const [chatConfig, setChatConfig] = useState(null);

  // Citation Inspector Modal
  const [activeCitation, setActiveCitation] = useState(null);

  // Retrieval Settings
  const [retrievalMode, setRetrievalMode] = useState('hybrid');
  const [enableRewriting, setEnableRewriting] = useState(true);
  const [topK, setTopK] = useState(4);
  const [ragStatus, setRagStatus] = useState(null);

  // Inspector State (Phase 4)
  const [consoleQuery, setConsoleQuery] = useState('');
  const [consoleData, setConsoleData] = useState(null);
  const [consoleView, setConsoleView] = useState('results');
  const [methodsComparison, setMethodsComparison] = useState(null);
  const [loadingConsole, setLoadingConsole] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  // Load chat & RAG config
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const [cfg, status] = await Promise.all([
          chatService.getConfig(),
          ragService.getStatus(),
        ]);
        setChatConfig(cfg);
        setRagStatus(status);
      } catch (err) {
        console.error('Failed to load chat configuration:', err);
      }
    };
    loadConfig();
  }, []);

  // Guarded version change notification (prevents duplicate initial/re-selection messages)
  const prevVersionRef = useRef(selectedVersion);
  useEffect(() => {
    if (prevVersionRef.current !== selectedVersion) {
      prevVersionRef.current = selectedVersion;
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: `*Context scope switched to **NexaDesk ${selectedVersion}**.* Knowledge retrieval and inference are strictly bounded to ${selectedVersion} documentation.`,
          citations: [],
          abstained: false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    }
  }, [selectedVersion]);

  // Simulated 3-stage generation progress
  useEffect(() => {
    let t1, t2;
    if (sending) {
      setGenerationStep(1);
      t1 = setTimeout(() => setGenerationStep(2), 700);
      t2 = setTimeout(() => setGenerationStep(3), 1600);
    } else {
      setGenerationStep(1);
    }
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [sending]);

  // Version-grounded sample customer inquiries
  const sampleInquiries = {
    'v1.0': [
      "Can I schedule automated report exports?",
      "What pricing plans and agent seats are available?",
      "How does email ticket ingestion work?",
      "What user roles are supported in v1.0?"
    ],
    'v2.0': [
      "Can I schedule automated report exports?",
      "How do round-robin ticket assignment rules work?",
      "Can I connect NexaDesk to Slack channels via webhooks?",
      "What is the annual billing discount?"
    ],
    'v3.0': [
      "Can I schedule automated report exports?",
      "What is the NexaDesk AI Copilot and NexaFlow Studio?",
      "What are the Enterprise SAML SSO and audit capabilities?",
      "What are the Scale tier quotas and priority SLA response times?"
    ]
  };

  // Submit enquiry to RAG pipeline
  const handleSendEnquiry = async (textToSend = inputQuery) => {
    const q = (textToSend || inputQuery).trim();
    if (!q || sending) return;

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
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: res.answer,
        citations: res.citations || [],
        abstained: res.abstained || false,
        rewritten_query: res.rewritten_query,
        latency_ms: res.latency_ms,
        model_used: res.model_used || 'qwen3.5:4b (ollama)',
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
          content: `⚠️ Error executing RAG inference: ${err.message || 'Server error'}. Ensure the backend and Ollama daemon are active.`,
          citations: [],
          abstained: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleResetChat = () => {
    const newId = `conv_${Date.now()}`;
    setConversationId(newId);
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: `Conversation restarted. I am your NexaDesk AI Assistant for **${selectedVersion}**. How can I help you today?`,
        citations: [],
        abstained: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
    ]);
  };

  // Inspector handlers (Phase 4)
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
      {/* 1. Mode Switcher & Workspace Bar */}
      <div className="bg-canvas-card rounded-2xl border border-white/[0.08] p-3 sm:p-4 shadow-dark-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-1.5 bg-canvas-void/80 p-1 rounded-xl border border-white/[0.06] self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'chat'
                ? 'bg-violetAccent text-white shadow-glow-violet'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles size={14} />
            <span>AI Support Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab('inspector')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'inspector'
                ? 'bg-violetAccent text-white shadow-glow-violet'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Terminal size={14} />
            <span>Hybrid Retrieval Inspector</span>
          </button>
        </div>

        <div className="flex items-center space-x-2.5 flex-wrap">
          {/* Active Version Selector */}
          <div className="flex items-center bg-canvas-void/80 border border-white/[0.06] p-0.5 rounded-xl text-xs">
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider px-2">Scope:</span>
            {['v1.0', 'v2.0', 'v3.0'].map((ver) => (
              <button
                key={ver}
                onClick={() => setSelectedVersion(ver)}
                className={`px-2 py-1 text-xs font-mono font-bold rounded-lg transition-all ${
                  selectedVersion === ver
                    ? 'bg-violetAccent/20 text-violetAccent-light border border-violetAccent/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {ver}
              </button>
            ))}
          </div>

          {/* New Thread Action */}
          {activeTab === 'chat' && (
            <button
              onClick={handleResetChat}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-400 hover:text-roseAccent hover:bg-roseAccent/10 border border-white/[0.07] rounded-xl bg-canvas-card transition-colors"
              title="Reset conversation thread"
            >
              <Trash2 size={13} />
              <span className="hidden sm:inline">New Thread</span>
            </button>
          )}
        </div>
      </div>

      {/* =========================================================================
          TAB 1: Conversational Customer Support AI
          ========================================================================= */}
      {activeTab === 'chat' && (
        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] shadow-dark-card flex flex-col h-[740px] overflow-hidden">
          {/* Workspace Sub-header */}
          <div className="px-5 py-3 border-b border-white/[0.07] bg-canvas-void/40 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violetAccent to-blueAccent p-[1px] shadow-glow-violet flex-shrink-0">
                <div className="w-full h-full bg-canvas-card rounded-[7px] flex items-center justify-center">
                  <Bot className="w-4 h-4 text-violetAccent-light" />
                </div>
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold text-sm text-white tracking-tight">
                    NexaDesk Intelligence Core
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-emeraldAccent/15 text-emeraldAccent border border-emeraldAccent/25 font-bold">
                    Grounded RAG
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Strictly bounded to <span className="font-semibold text-violetAccent-light font-mono">NexaDesk {selectedVersion}</span> · Hallucination Prevention Active
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2 text-xs font-mono">
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-white/[0.04] text-slate-300 border border-white/[0.07] text-[11px]">
                <span className="w-1.5 h-1.5 rounded-full bg-emeraldAccent animate-pulse" />
                <span>Qwen 3.5 4B (Ollama)</span>
              </span>
            </div>
          </div>

          {/* Conversation Stream */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-canvas-base/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${
                  msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                {/* Avatar */}
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs flex-shrink-0 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-tr from-violetAccent to-blueAccent text-white'
                      : 'bg-canvas-void border border-white/[0.1] text-violetAccent-light'
                  }`}
                >
                  {msg.role === 'user' ? <User size={14} /> : <Sparkles size={14} />}
                </div>

                {/* Message Bubble Container */}
                <div
                  className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 sm:p-5 space-y-3 ${
                    msg.role === 'user'
                      ? 'bg-canvas-card border border-violet-500/30 text-white rounded-tr-none shadow-dark-card'
                      : 'bg-canvas-card border border-white/[0.08] text-slate-100 rounded-tl-none shadow-dark-sm'
                  }`}
                >
                  {/* Rewritten Query Sub-pill */}
                  {msg.rewritten_query && msg.rewritten_query !== msg.content && (
                    <div className="text-[11px] text-slate-300 bg-canvas-void/90 px-3 py-1.5 rounded-xl border border-white/[0.08] flex items-center space-x-2 font-mono">
                      <Terminal size={12} className="text-violetAccent-light flex-shrink-0" />
                      <span className="text-slate-400">Interpreted query:</span>
                      <span className="text-white font-semibold truncate">{msg.rewritten_query}</span>
                    </div>
                  )}

                  {/* Main Answer Content with Markdown rendering */}
                  <div className="leading-relaxed font-sans text-[13px] sm:text-[14px] text-slate-100">
                    <MarkdownRenderer content={msg.content} />
                  </div>

                  {/* Grounded Abstention Notice */}
                  {msg.abstained && (
                    <div className="mt-3 p-3.5 rounded-xl bg-amberAccent/10 border border-amberAccent/35 text-amberAccent text-xs flex items-start space-x-3">
                      <ShieldAlert size={18} className="text-amberAccent flex-shrink-0 mt-0.5" />
                      <div className="space-y-1.5 flex-1">
                        <p className="font-bold text-xs text-amberAccent">
                          Strict Grounding Safeguard Triggered
                        </p>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans">
                          This feature is undocumented in NexaDesk {selectedVersion}. The system abstains to guarantee 0% hallucination and prevent misleading support guidance.
                        </p>
                        <button
                          onClick={() => alert(`Escalated enquiry to NexaDesk Tier-2 Support Ticket under session ${conversationId}.`)}
                          className="mt-2 inline-flex items-center space-x-1.5 px-3 py-1.5 bg-amberAccent hover:bg-amberAccent-hover text-canvas-void rounded-lg text-xs font-bold transition-colors shadow-sm"
                        >
                          <span>Escalate to Human Support Specialist</span>
                          <ArrowRight size={12} />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Verifiable Source Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-3 border-t border-white/[0.06] space-y-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5 font-mono">
                        <BookOpen size={12} className="text-cyan-400" />
                        <span>Verifiable Knowledge Sources ({msg.citations.length}):</span>
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {msg.citations.map((cite) => (
                          <button
                            key={cite.citation_id}
                            onClick={() => setActiveCitation(cite)}
                            className="text-xs font-mono font-medium px-2.5 py-1.5 bg-blue-950/40 hover:bg-blue-900/50 hover:border-blue-400/60 border border-blue-500/30 rounded-lg text-blue-200 transition-all flex items-center space-x-2 group shadow-sm"
                            title="Inspect source snippet"
                          >
                            <FileText size={12} className="text-blue-400 group-hover:text-cyan-300 transition-colors" />
                            <span className="font-semibold truncate max-w-[170px]">{cite.document_name}</span>
                            <span className="text-blue-400/60">·</span>
                            <span className="text-blue-300 text-[11px]">p.{cite.page_number}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Footer Meta & Copy */}
                  <div className="flex items-center justify-between text-[10px] pt-1 border-t border-white/[0.04] text-slate-500 font-mono">
                    <div className="flex items-center space-x-2">
                      <span>{msg.timestamp}</span>
                      {msg.role === 'assistant' && (
                        <button
                          onClick={() => handleCopyAnswer(msg.id, msg.content)}
                          className="text-slate-400 hover:text-white flex items-center space-x-1 transition-colors"
                          title="Copy answer"
                        >
                          {copiedMessageId === msg.id ? (
                            <>
                              <Check size={11} className="text-emeraldAccent" />
                              <span className="text-emeraldAccent font-bold">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={11} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>

                    {msg.latency_ms && (
                      <span className="text-slate-500">
                        ⚡ {msg.latency_ms} ms · {msg.model_used}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* 3-Stage Thinking Indicator */}
            {sending && (
              <div className="flex items-start space-x-3 py-2">
                <div className="w-7 h-7 rounded-lg bg-canvas-void border border-white/[0.1] text-violetAccent-light flex items-center justify-center flex-shrink-0 animate-pulse">
                  <Bot size={15} />
                </div>
                <div className="bg-canvas-card border border-white/[0.08] rounded-2xl rounded-tl-none p-3.5 space-y-2 max-w-md shadow-dark-sm">
                  <div className="flex items-center space-x-2 text-xs font-semibold text-white">
                    <RefreshCw size={12} className="animate-spin text-violetAccent-light" />
                    <span>NexaDesk RAG Pipeline In Progress...</span>
                  </div>

                  <div className="space-y-1.5 text-[11px] font-mono">
                    <div className={`flex items-center space-x-2 ${generationStep >= 1 ? 'text-white font-semibold' : 'text-slate-500'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 1 ? 'bg-violetAccent' : 'bg-slate-600'}`} />
                      <span>1. Rewriting query intent with Qwen 3.5 4B</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${generationStep >= 2 ? 'text-white font-semibold' : 'text-slate-500'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 2 ? 'bg-blueAccent' : 'bg-slate-600'}`} />
                      <span>2. Querying ChromaDB ({selectedVersion}) & BM25Okapi</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${generationStep >= 3 ? 'text-white font-semibold' : 'text-slate-500'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 3 ? 'bg-emeraldAccent' : 'bg-slate-600'}`} />
                      <span>3. Synthesizing grounded answer with citations</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Customer Queries for Active Version */}
          <div className="px-5 py-3 bg-canvas-void/50 border-t border-white/[0.07]">
            <div className="flex items-center space-x-1.5 mb-2 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">
              <HelpCircle size={12} className="text-violetAccent-light" />
              <span>Suggested questions for NexaDesk {selectedVersion}:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {(sampleInquiries[selectedVersion] || []).map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendEnquiry(sample)}
                  disabled={sending}
                  className="text-xs px-3 py-1.5 bg-canvas-card hover:bg-violet-950/30 hover:border-violet-500/40 border border-white/[0.08] text-slate-300 hover:text-white rounded-xl transition-all disabled:opacity-50 text-left font-sans flex items-center space-x-2 group shadow-sm"
                >
                  <span className="text-violetAccent-light font-mono text-[11px] group-hover:translate-x-0.5 transition-transform">→</span>
                  <span>{sample}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Message Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendEnquiry();
            }}
            className="p-3.5 border-t border-white/[0.07] bg-canvas-card flex items-center space-x-3"
          >
            <div className="relative flex-1">
              <input
                type="text"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                placeholder={`Ask any customer question grounded in NexaDesk ${selectedVersion}...`}
                disabled={sending}
                className="w-full text-xs sm:text-sm bg-canvas-void border border-white/[0.1] rounded-xl pl-4 pr-24 py-3 text-white placeholder:text-slate-500 focus:outline-none focus:border-violetAccent focus:ring-1 focus:ring-violetAccent"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-500 hidden sm:inline">
                Scope: {selectedVersion}
              </span>
            </div>

            <button
              type="submit"
              disabled={!inputQuery.trim() || sending}
              className="px-5 py-3 rounded-xl bg-violetAccent hover:bg-violetAccent-hover text-white font-bold text-xs shadow-glow-violet disabled:opacity-40 transition-all flex items-center space-x-2 flex-shrink-0"
            >
              <span>Submit</span>
              <Send size={13} />
            </button>
          </form>
        </div>
      )}

      {/* =========================================================================
          TAB 2: Hybrid Retrieval Inspector Console (Phase 4 View)
          ========================================================================= */}
      {activeTab === 'inspector' && (
        <div className="bg-canvas-card rounded-2xl border border-white/[0.08] shadow-dark-card p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/[0.07] gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <Terminal size={17} className="text-violetAccent-light" />
                <h3 className="text-base font-bold text-white tracking-tight">
                  Hybrid Retrieval & Reciprocal Rank Fusion (RRF) Inspector
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Inspect raw query rewriting, Dense vector scores vs BM25 sparse lexical ranks, and 3-way retrieval strategy comparisons.
              </p>
            </div>
            <span className="text-xs font-mono font-bold px-3 py-1 rounded-lg bg-violetAccent/10 text-violetAccent-light border border-violetAccent/20">
              Scope: {selectedVersion}
            </span>
          </div>

          {/* Console Input Bar */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <input
              type="text"
              value={consoleQuery}
              onChange={(e) => setConsoleQuery(e.target.value)}
              placeholder="Enter customer enquiry to inspect retrieval..."
              className="flex-1 text-xs bg-canvas-void border border-white/[0.1] rounded-xl px-4 py-2.5 text-white placeholder:text-slate-500 focus:outline-none focus:border-violetAccent"
            />
            <button
              onClick={() => handleRunConsole()}
              disabled={!consoleQuery.trim() || loadingConsole}
              className="px-4 py-2.5 bg-violetAccent hover:bg-violetAccent-hover text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50 shadow-glow-violet"
            >
              <Layers size={13} />
              <span>Inspect Hybrid RRF</span>
            </button>
            <button
              onClick={() => handleRunCompareMethods()}
              disabled={!consoleQuery.trim() || loadingConsole}
              className="px-4 py-2.5 bg-canvas-void hover:bg-white/[0.08] text-slate-200 border border-white/[0.1] font-bold rounded-xl text-xs flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
            >
              <Activity size={13} />
              <span>Compare 3 Strategies</span>
            </button>
          </div>

          {/* Output Display */}
          {loadingConsole && (
            <div className="py-16 text-center text-xs text-slate-400 space-y-2">
              <RefreshCw size={22} className="animate-spin text-violetAccent-light mx-auto" />
              <p className="font-semibold text-slate-300">Executing Retrieval Fusion over {selectedVersion} index...</p>
            </div>
          )}

          {!loadingConsole && consoleView === 'results' && consoleData && (
            <div className="space-y-4">
              <div className="bg-canvas-void p-4 rounded-xl border border-white/[0.07] text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">Query Rewriting & Intent Analysis</span>
                  <span className="font-mono text-[11px] text-violetAccent-light">Model: Qwen 3.5 4B</span>
                </div>
                <p className="text-slate-300 font-mono"><strong>Rewritten Query:</strong> "{consoleData.rewritten_query}"</p>
                <p className="text-slate-400 font-mono"><strong>Detected Intent:</strong> {consoleData.diagnostics?.intent_detected || 'Product Feature Inquiry'}</p>
                <p className="text-slate-400 font-mono"><strong>Keywords:</strong> {consoleData.search_keywords?.join(', ')}</p>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
                  Top RRF Ranked Document Chunks ({consoleData.results?.length || 0})
                </h4>
                {consoleData.results?.map((r, i) => (
                  <div key={i} className="bg-canvas-void p-4 rounded-xl border border-white/[0.06] text-xs space-y-2">
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-white font-bold">{r.document_name} (§ {r.section_title})</span>
                      <span className="font-mono px-2 py-0.5 rounded bg-violetAccent/20 text-violetAccent-light text-[11px] font-bold border border-violetAccent/30">
                        RRF Score: {(r.rrf_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px] font-mono whitespace-pre-wrap bg-canvas-card p-3 rounded-lg border border-white/[0.06] leading-relaxed">
                      {r.text_content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loadingConsole && consoleView === 'compare_methods' && methodsComparison && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="bg-canvas-void p-4 rounded-xl border border-white/[0.06] space-y-3">
                <span className="font-bold text-slate-300 uppercase block text-[11px] tracking-wider">
                  1. Raw Dense Retrieval
                </span>
                {methodsComparison.raw_dense_results?.map((r, i) => (
                  <div key={i} className="bg-canvas-card p-3 rounded-lg border border-white/[0.06] space-y-1">
                    <p className="font-semibold text-white truncate">{r.document_name}</p>
                    <p className="text-[10px] text-slate-500">Cosine Sim: {r.dense_score?.toFixed(3)}</p>
                  </div>
                ))}
              </div>

              <div className="bg-canvas-void p-4 rounded-xl border border-white/[0.06] space-y-3">
                <span className="font-bold text-blueAccent uppercase block text-[11px] tracking-wider">
                  2. Rewritten Dense
                </span>
                {methodsComparison.rewritten_dense_results?.map((r, i) => (
                  <div key={i} className="bg-canvas-card p-3 rounded-lg border border-white/[0.06] space-y-1">
                    <p className="font-semibold text-white truncate">{r.document_name}</p>
                    <p className="text-[10px] text-blueAccent">Cosine Sim: {r.dense_score?.toFixed(3)}</p>
                  </div>
                ))}
              </div>

              <div className="bg-canvas-void p-4 rounded-xl border border-violetAccent/30 space-y-3">
                <span className="font-bold text-violetAccent-light uppercase block text-[11px] tracking-wider">
                  3. Rewritten Hybrid (RRF)
                </span>
                {methodsComparison.rewritten_hybrid_results?.map((r, i) => (
                  <div key={i} className="bg-canvas-card p-3 rounded-lg border border-violetAccent/20 space-y-1">
                    <p className="font-semibold text-white truncate">{r.document_name}</p>
                    <p className="text-[10px] text-violetAccent-light font-bold">RRF: {(r.rrf_score * 100).toFixed(1)}%</p>
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
        <div className="fixed inset-0 bg-canvas-void/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-canvas-card rounded-2xl shadow-dark-elevated max-w-lg w-full border border-white/[0.1] overflow-hidden space-y-4 p-6">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.07]">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-violetAccent/15 text-violetAccent-light border border-violetAccent/25">
                  <BookOpen size={16} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white tracking-tight">Verifiable Source Citation</h4>
                  <span className="text-[11px] text-slate-400 font-mono">ChromaDB Chunk Snippet</span>
                </div>
              </div>
              <button
                onClick={() => setActiveCitation(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-canvas-void p-3 rounded-xl border border-white/[0.06] font-mono text-[11px]">
                <div><span className="text-slate-500">Document:</span> <span className="font-semibold text-slate-200 block truncate">{activeCitation.document_name}</span></div>
                <div><span className="text-slate-500">Page:</span> <span className="font-semibold text-slate-200 block">p. {activeCitation.page_number}</span></div>
                <div><span className="text-slate-500">Section:</span> <span className="font-semibold text-slate-200 block truncate">{activeCitation.section_title}</span></div>
                <div><span className="text-slate-500">Format:</span> <span className="font-semibold uppercase text-violetAccent-light block">{activeCitation.document_type}</span></div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1.5 font-mono">
                  Source Text Content:
                </span>
                <p className="p-3.5 bg-canvas-void border border-white/[0.06] rounded-xl text-slate-200 font-mono text-xs leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
                  {activeCitation.snippet}
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-white/[0.07] flex justify-end">
              <button
                onClick={() => setActiveCitation(null)}
                className="px-4 py-2 bg-white/[0.06] hover:bg-white/[0.1] text-slate-200 font-semibold rounded-xl text-xs transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
