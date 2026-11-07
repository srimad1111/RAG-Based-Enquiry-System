import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  User,
  FileText,
  Terminal,
  Trash2,
  X,
  Copy,
  Check,
  ShieldAlert,
  ArrowRight,
  BookOpen,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Layers,
  Activity,
} from 'lucide-react';
import { useSystem } from '../../context/SystemContext';
import chatService from '../../services/chatService';
import ragService from '../../services/ragService';
import MarkdownRenderer from '../common/MarkdownRenderer';

export function ChatInterface() {
  const { selectedVersion, setSelectedVersion } = useSystem();

  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [showInspector, setShowInspector] = useState(false);

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

  // Citation Inspector Modal
  const [activeCitation, setActiveCitation] = useState(null);

  // Inspector state
  const [inspectorQuery, setInspectorQuery] = useState('');
  const [inspectorData, setInspectorData] = useState(null);
  const [inspectorLoading, setInspectorLoading] = useState(false);
  const [methodsComparison, setMethodsComparison] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

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
        retrieval_mode: 'hybrid',
        top_k: 4,
        enable_rewriting: true,
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

  const handleRunInspector = async (q = inspectorQuery) => {
    if (!q.trim()) return;
    setInspectorLoading(true);
    try {
      const res = await ragService.retrieveHybrid({
        customer_question: q,
        product_version: selectedVersion,
        enable_query_rewriting: true,
        retrieval_mode: 'hybrid',
        top_k: 4,
      });
      setInspectorData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectorLoading(false);
    }
  };

  const handleCompareMethods = async (q = inspectorQuery) => {
    if (!q.trim()) return;
    setInspectorLoading(true);
    try {
      const res = await ragService.compareRetrievalMethods({
        customer_question: q,
        product_version: selectedVersion,
        top_k: 3,
      });
      setMethodsComparison(res);
    } catch (err) {
      console.error(err);
    } finally {
      setInspectorLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4 text-slate-100">
      {/* Centered, Clean Support Workspace Card */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] shadow-card flex flex-col h-[740px] overflow-hidden">
        {/* Clean Workspace Header */}
        <div className="px-5 py-3.5 border-b border-white/[0.08] bg-[#141E33] flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-accent-blue to-accent-violet p-[1px] flex-shrink-0 shadow-glow-blue">
              <div className="w-full h-full bg-[#141E33] rounded-[11px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-accent-blue" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="font-semibold text-sm text-white">
                  NexaDesk Support Assistant
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-accent-blue/15 text-accent-blue font-bold">
                  {selectedVersion}
                </span>
              </div>
              <p className="text-[11px] text-slate-300">
                Grounded in official documentation · Hallucination safeguard active
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Optional Expandable Retrieval Inspector Toggle */}
            <button
              onClick={() => setShowInspector(!showInspector)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs transition-colors border ${
                showInspector
                  ? 'bg-accent-blue/15 text-accent-blue border-accent-blue/30 font-medium'
                  : 'text-slate-300 hover:text-white hover:bg-white/[0.04] border-white/[0.08]'
              }`}
              title="Inspect dense & BM25 retrieval fusion"
            >
              <Terminal size={13} />
              <span className="hidden sm:inline">Inspect Retrieval</span>
              {showInspector ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>

            {/* Reset Chat */}
            <button
              onClick={handleResetChat}
              className="p-2 text-slate-300 hover:text-white hover:bg-white/[0.04] rounded-xl border border-white/[0.08] transition-colors"
              title="New conversation thread"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-[#0B1020]/60">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3 ${
                msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs flex-shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-accent-blue text-white'
                    : 'bg-gradient-to-tr from-accent-blue to-accent-violet text-white shadow-glow-blue'
                }`}
              >
                {msg.role === 'user' ? <User size={14} /> : <Sparkles size={14} />}
              </div>

              {/* Message Bubble Container */}
              <div
                className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 sm:p-5 space-y-3 ${
                  msg.role === 'user'
                    ? 'bg-[#192640] border border-white/[0.1] text-white rounded-tr-none'
                    : 'bg-[#141E33] border border-white/[0.08] text-slate-100 rounded-tl-none shadow-card'
                }`}
              >
                {/* Main Answer Content with Full Markdown Rendering */}
                <div className="leading-relaxed font-sans text-xs sm:text-[13px] text-white">
                  <MarkdownRenderer content={msg.content} />
                </div>

                {/* Grounded Abstention Notice */}
                {msg.abstained && (
                  <div className="mt-3 p-3.5 rounded-xl bg-accent-amber/15 border border-accent-amber/35 text-accent-amber text-xs flex items-start space-x-3">
                    <ShieldAlert size={16} className="text-accent-amber flex-shrink-0 mt-0.5" />
                    <div className="space-y-1.5 flex-1">
                      <p className="font-semibold text-xs text-accent-amber">
                        Feature Undocumented in NexaDesk {selectedVersion}
                      </p>
                      <p className="text-xs text-slate-200 leading-relaxed font-sans">
                        This capability is not documented in NexaDesk {selectedVersion}. The assistant abstained to prevent misleading answers.
                      </p>
                      <button
                        onClick={() => alert(`Escalated enquiry to NexaDesk Support Ticket under session ${conversationId}.`)}
                        className="mt-1 inline-flex items-center space-x-1 px-3 py-1 bg-accent-amber text-black font-semibold rounded-lg text-xs transition-colors"
                      >
                        <span>Escalate to Human Specialist</span>
                        <ArrowRight size={11} />
                      </button>
                    </div>
                  </div>
                )}

                {/* Verifiable Source Citations (Visually Distinct Compact Cards) */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2.5 border-t border-white/[0.06] space-y-1.5">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5 font-mono">
                      <BookOpen size={11} className="text-accent-blue" />
                      <span>Verifiable Sources ({msg.citations.length}):</span>
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cite) => (
                        <button
                          key={cite.citation_id}
                          onClick={() => setActiveCitation(cite)}
                          className="text-xs font-mono px-2.5 py-1 bg-[#192640] hover:bg-[#213354] border border-white/[0.08] rounded-lg text-accent-blue transition-all flex items-center space-x-1.5 group"
                          title="Click to inspect citation snippet"
                        >
                          <FileText size={11} className="text-accent-blue group-hover:text-white transition-colors" />
                          <span className="truncate max-w-[150px] font-medium text-slate-200">{cite.document_name}</span>
                          <span className="text-slate-500">·</span>
                          <span className="text-slate-400 text-[11px]">p.{cite.page_number}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Footer Meta & Copy */}
                <div className="flex items-center justify-between text-[11px] pt-1 text-slate-400 font-mono">
                  <div className="flex items-center space-x-2">
                    <span>{msg.timestamp}</span>
                    {msg.role === 'assistant' && (
                      <button
                        onClick={() => handleCopyAnswer(msg.id, msg.content)}
                        className="text-slate-400 hover:text-white flex items-center space-x-1 transition-colors"
                        title="Copy answer to clipboard"
                      >
                        {copiedMessageId === msg.id ? (
                          <>
                            <Check size={11} className="text-accent-emerald" />
                            <span className="text-accent-emerald font-medium">Copied</span>
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
                    <span className="text-slate-400 text-[10px]">
                      ⚡ {msg.latency_ms} ms · {msg.model_used}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* 3-Stage Progress Indicator */}
          {sending && (
            <div className="flex items-start space-x-3 py-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-accent-blue to-accent-violet text-white flex items-center justify-center flex-shrink-0 animate-pulse">
                <Sparkles size={14} />
              </div>
              <div className="bg-[#141E33] border border-white/[0.08] rounded-2xl rounded-tl-none p-3.5 space-y-2 max-w-sm shadow-card">
                <div className="flex items-center space-x-2 text-xs font-semibold text-white">
                  <RefreshCw size={12} className="animate-spin text-accent-blue" />
                  <span>Synthesizing Answer...</span>
                </div>
                <div className="space-y-1 text-[11px] text-slate-300 font-mono">
                  <div className={`flex items-center space-x-1.5 ${generationStep >= 1 ? 'text-white' : 'text-slate-500'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 1 ? 'bg-accent-blue' : 'bg-slate-600'}`} />
                    <span>Rewriting intent with Qwen 3.5 4B</span>
                  </div>
                  <div className={`flex items-center space-x-1.5 ${generationStep >= 2 ? 'text-white' : 'text-slate-500'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 2 ? 'bg-accent-violet' : 'bg-slate-600'}`} />
                    <span>Retrieving from ChromaDB ({selectedVersion}) & BM25</span>
                  </div>
                  <div className={`flex items-center space-x-1.5 ${generationStep >= 3 ? 'text-white' : 'text-slate-500'}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${generationStep >= 3 ? 'bg-accent-emerald' : 'bg-slate-600'}`} />
                    <span>Synthesizing grounded citations</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Compact Suggested Questions Chips */}
        <div className="px-5 py-2.5 bg-[#141E33] border-t border-white/[0.08]">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            <span className="text-[11px] text-slate-400 whitespace-nowrap mr-1 font-mono">
              Suggested:
            </span>
            {(sampleInquiries[selectedVersion] || []).map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSendEnquiry(sample)}
                disabled={sending}
                className="text-xs px-2.5 py-1 bg-[#192640] hover:bg-[#213354] text-slate-200 hover:text-white border border-white/[0.08] rounded-lg transition-colors whitespace-nowrap disabled:opacity-50"
              >
                {sample}
              </button>
            ))}
          </div>
        </div>

        {/* Message Input Composer */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendEnquiry();
          }}
          className="p-3.5 border-t border-white/[0.08] bg-[#141E33] flex items-center space-x-2.5"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder={`Ask any customer question grounded in NexaDesk ${selectedVersion}...`}
              disabled={sending}
              className="w-full text-xs sm:text-sm bg-[#192640] border border-white/[0.08] rounded-xl pl-4 pr-24 py-3 text-white placeholder:text-slate-400 focus:outline-none focus:border-accent-blue"
            />
            <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[11px] font-mono text-slate-400 hidden sm:inline">
              Scope: {selectedVersion}
            </span>
          </div>

          <button
            type="submit"
            disabled={!inputQuery.trim() || sending}
            className="px-4 py-3 rounded-xl bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold text-xs shadow-glow-blue disabled:opacity-40 transition-all flex items-center space-x-1.5 flex-shrink-0"
          >
            <span>Send</span>
            <Send size={13} />
          </button>
        </form>
      </div>

      {/* Optional Expandable Retrieval Inspector (Kept Cleanly Collapsible) */}
      {showInspector && (
        <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 shadow-card space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
            <div className="flex items-center space-x-2">
              <Terminal size={15} className="text-accent-blue" />
              <h3 className="text-sm font-semibold text-white">
                Hybrid Retrieval & Fusion Inspector
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-300">Scope: {selectedVersion}</span>
          </div>

          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={inspectorQuery}
              onChange={(e) => setInspectorQuery(e.target.value)}
              placeholder="Enter enquiry to inspect RRF ranking..."
              className="flex-1 text-xs bg-[#192640] border border-white/[0.08] rounded-xl px-3.5 py-2 text-white placeholder:text-slate-400 focus:outline-none focus:border-accent-blue"
            />
            <button
              onClick={() => handleRunInspector()}
              disabled={!inspectorQuery.trim() || inspectorLoading}
              className="px-3.5 py-2 bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold text-xs rounded-xl transition-colors disabled:opacity-50 flex items-center space-x-1.5"
            >
              <Layers size={13} />
              <span>Inspect Fusion</span>
            </button>
            <button
              onClick={() => handleCompareMethods()}
              disabled={!inspectorQuery.trim() || inspectorLoading}
              className="px-3.5 py-2 bg-[#192640] hover:bg-[#213354] text-white border border-white/[0.08] font-semibold text-xs rounded-xl transition-colors disabled:opacity-50 flex items-center space-x-1.5"
            >
              <Activity size={13} />
              <span>Compare 3 Strategies</span>
            </button>
          </div>

          {inspectorLoading && (
            <div className="py-8 text-center text-xs text-slate-300 space-y-2">
              <RefreshCw size={18} className="animate-spin text-accent-blue mx-auto" />
              <p>Executing Retrieval Fusion over {selectedVersion} index...</p>
            </div>
          )}

          {!inspectorLoading && inspectorData && (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-[#192640] rounded-xl border border-white/[0.08] space-y-1 font-mono text-[11px]">
                <p className="text-white"><strong>Rewritten Query:</strong> "{inspectorData.rewritten_query}"</p>
                <p className="text-slate-300"><strong>Detected Intent:</strong> {inspectorData.diagnostics?.intent_detected || 'Feature Inquiry'}</p>
              </div>

              <div className="space-y-2">
                <span className="text-[11px] font-mono text-slate-300 block">
                  Top Ranked Chunks ({inspectorData.results?.length || 0}):
                </span>
                {inspectorData.results?.map((r, i) => (
                  <div key={i} className="p-3 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-white">{r.document_name} (§ {r.section_title})</span>
                      <span className="font-mono text-accent-blue text-[11px]">
                        RRF: {(r.rrf_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px] font-mono leading-relaxed line-clamp-3">
                      {r.text_content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!inspectorLoading && methodsComparison && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono pt-1">
              <div className="p-3 rounded-xl bg-[#192640] border border-white/[0.08] space-y-2">
                <span className="font-semibold text-slate-300 block text-[11px]">1. Raw Dense</span>
                {methodsComparison.raw_dense_results?.map((r, i) => (
                  <div key={i} className="p-2 bg-[#141E33] rounded-lg text-[11px] truncate">
                    <p className="text-white truncate font-sans">{r.document_name}</p>
                    <span className="text-slate-400 text-[10px]">Sim: {r.dense_score?.toFixed(3)}</span>
                  </div>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-[#192640] border border-white/[0.08] space-y-2">
                <span className="font-semibold text-accent-blue block text-[11px]">2. Rewritten Dense</span>
                {methodsComparison.rewritten_dense_results?.map((r, i) => (
                  <div key={i} className="p-2 bg-[#141E33] rounded-lg text-[11px] truncate">
                    <p className="text-white truncate font-sans">{r.document_name}</p>
                    <span className="text-accent-blue text-[10px]">Sim: {r.dense_score?.toFixed(3)}</span>
                  </div>
                ))}
              </div>

              <div className="p-3 rounded-xl bg-[#192640] border border-accent-blue/30 space-y-2">
                <span className="font-semibold text-accent-violet block text-[11px]">3. Rewritten Hybrid RRF</span>
                {methodsComparison.rewritten_hybrid_results?.map((r, i) => (
                  <div key={i} className="p-2 bg-[#141E33] rounded-lg text-[11px] truncate border border-accent-blue/20">
                    <p className="text-white truncate font-sans">{r.document_name}</p>
                    <span className="text-accent-emerald text-[10px] font-bold">RRF: {(r.rrf_score * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Citation Inspector Modal */}
      {activeCitation && (
        <div className="fixed inset-0 bg-[#070A14]/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-[#141E33] rounded-2xl shadow-modal max-w-lg w-full border border-white/[0.1] p-6 space-y-4 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-accent-blue/15 text-accent-blue border border-accent-blue/25">
                  <BookOpen size={16} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Verifiable Source Citation</h3>
                  <span className="text-[11px] text-slate-300 font-mono">Retrieved Knowledge Chunk</span>
                </div>
              </div>
              <button
                onClick={() => setActiveCitation(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-[#192640] p-3 rounded-xl border border-white/[0.08] font-mono text-[11px]">
                <div><span className="text-slate-400">Document:</span> <span className="font-semibold text-white block truncate">{activeCitation.document_name}</span></div>
                <div><span className="text-slate-400">Page:</span> <span className="font-semibold text-white block">p. {activeCitation.page_number}</span></div>
                <div><span className="text-slate-400">Section:</span> <span className="font-semibold text-white block truncate">{activeCitation.section_title}</span></div>
                <div><span className="text-slate-400">Format:</span> <span className="font-semibold uppercase text-accent-blue block">{activeCitation.document_type}</span></div>
              </div>

              <div>
                <span className="text-[10px] font-semibold text-slate-300 uppercase tracking-wider block mb-1.5 font-mono">
                  Extracted Context Text:
                </span>
                <p className="p-3.5 bg-[#192640] border border-white/[0.08] rounded-xl text-slate-100 font-mono text-xs leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto">
                  {activeCitation.snippet}
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-white/[0.08] flex justify-end">
              <button
                onClick={() => setActiveCitation(null)}
                className="px-4 py-2 bg-[#192640] hover:bg-[#213354] text-white font-semibold rounded-xl text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
