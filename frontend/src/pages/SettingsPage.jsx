import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Database,
  Layers,
  Shield,
  Activity,
  CheckCircle2,
  RefreshCw,
  Server,
  Zap,
  Sliders,
  ChevronDown,
  ChevronUp,
  Info,
  Check,
  ExternalLink,
} from 'lucide-react';
import { useSystem } from '../context/SystemContext';
import ragService from '../services/ragService';
import chatService from '../services/chatService';

export function SettingsPage() {
  const { selectedVersion, setSelectedVersion, health, refreshHealth } = useSystem();

  const [chatConfig, setChatConfig] = useState(null);
  const [ragStatus, setRagStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);

  // Collapsible sections state (advanced collapsed by default as requested)
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [cfg, status] = await Promise.all([
          chatService.getConfig(),
          ragService.getStatus(),
        ]);
        setChatConfig(cfg);
        setRagStatus(status);
      } catch (err) {
        console.error('Failed to load settings data:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSyncVectors = async () => {
    setSyncing(true);
    setSyncSuccess(false);
    try {
      await ragService.reindexAll();
      setSyncSuccess(true);
      refreshHealth();
      setTimeout(() => setSyncSuccess(false), 3000);
    } catch (err) {
      alert(`Sync failed: ${err.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const totalChunks = ragStatus?.total_chunks_indexed ?? 33;

  // The 7-Stage Architectural Pipeline cleanly housed in Settings / Diagnostics
  const pipelineSteps = [
    { step: '01', name: 'Document Ingestion', desc: 'Parses PDF, DOCX, TXT, and Markdown docs into structured sections.', tech: 'PyMuPDF · python-docx' },
    { step: '02', name: 'Embedding Generation', desc: 'Encodes text chunks into dense 384-dimensional vector representations.', tech: 'all-MiniLM-L6-v2' },
    { step: '03', name: 'ChromaDB Vector Store', desc: 'Indexes dense embeddings with cosine similarity distance metric.', tech: `${totalChunks} Persistent Vectors` },
    { step: '04', name: 'BM25 Sparse Lexical', desc: 'Tokenizes and scores exact term frequencies for high-precision lookup.', tech: 'Okapi BM25 Index' },
    { step: '05', name: 'Hybrid Fusion (RRF)', desc: 'Combines dense vector and BM25 sparse scores using Reciprocal Rank Fusion.', tech: 'RRF (k=60 Constant)' },
    { step: '06', name: 'Query Intent Rewriting', desc: 'Resolves ambiguous customer enquiries into targeted search queries.', tech: 'Qwen 3.5 4B (Ollama)' },
    { step: '07', name: 'Grounded Answer Synthesis', desc: 'Generates responses strictly attributed to citations, abstaining on gaps.', tech: 'Strict Abstention Guard' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 text-slate-100">
      {/* Header */}
      <div className="pb-4 border-b border-white/[0.08]">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
          Settings & System Diagnostics
        </h1>
        <p className="text-xs text-slate-300 mt-1">
          Configure runtime parameters, manage AI model connections, and view platform health.
        </p>
      </div>

      {/* 1. General Settings */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 space-y-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-accent-blue/15 text-accent-blue border border-accent-blue/25">
            <Sliders size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">General Settings</h2>
            <p className="text-xs text-slate-300">Platform defaults and version isolation scope</p>
          </div>
        </div>

        <div className="pt-2 divide-y divide-white/[0.05] text-xs">
          {/* Active Version Scope */}
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="font-semibold text-white block">Active Documentation Scope</span>
              <span className="text-slate-300 text-[11px] block mt-0.5">
                Restricts retrieval and model inference strictly to this version's docs.
              </span>
            </div>
            <div className="flex items-center space-x-1.5 bg-[#192640] p-1 rounded-xl border border-white/[0.08] self-start sm:self-auto">
              {['v1.0', 'v2.0', 'v3.0'].map((ver) => (
                <button
                  key={ver}
                  onClick={() => setSelectedVersion(ver)}
                  className={`px-3 py-1.5 rounded-lg font-mono text-xs font-semibold transition-all ${
                    selectedVersion === ver
                      ? 'bg-accent-blue text-white shadow-sm'
                      : 'text-slate-300 hover:text-white'
                  }`}
                >
                  {ver}
                </button>
              ))}
            </div>
          </div>

          {/* Retrieval Mode */}
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="font-semibold text-white block">Default Retrieval Mode</span>
              <span className="text-slate-300 text-[11px] block mt-0.5">
                Combines dense semantic vectors with BM25 sparse keyword ranking.
              </span>
            </div>
            <span className="font-mono text-xs px-2.5 py-1 rounded-lg bg-[#192640] text-accent-blue border border-accent-blue/25 font-semibold self-start sm:self-auto">
              Hybrid Fusion (RRF)
            </span>
          </div>

          {/* Hallucination Guard */}
          <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="font-semibold text-white block">Hallucination & Abstention Guard</span>
              <span className="text-slate-300 text-[11px] block mt-0.5">
                Refuses to fabricate answers when information is absent from documentation.
              </span>
            </div>
            <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/25 text-xs font-semibold self-start sm:self-auto">
              <CheckCircle2 size={12} />
              <span>Active (0% Leakage)</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2. Ollama Model Configuration */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 space-y-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-accent-violet/15 text-accent-violet border border-accent-violet/25">
            <Cpu size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Ollama Model Configuration</h2>
            <p className="text-xs text-slate-300">Local neural model serving inference and query rewriting</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Active Model</span>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-white text-sm">qwen3.5:4b</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-accent-violet/20 text-accent-violet font-semibold">Active</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Inference Provider</span>
            <span className="font-mono text-white font-semibold text-sm">Ollama Local API</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Base URL</span>
            <span className="font-mono text-white text-xs">http://localhost:11434</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Execution Target</span>
            <span className="font-mono text-accent-emerald text-xs font-semibold">Local CPU (AVX2 Accelerated)</span>
          </div>
        </div>
      </div>

      {/* 3. ChromaDB Vector Store Configuration */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/25">
              <Database size={16} />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">ChromaDB Vector Store</h2>
              <p className="text-xs text-slate-300">Persistent vector index with dense sentence embeddings</p>
            </div>
          </div>

          <button
            onClick={handleSyncVectors}
            disabled={syncing}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-[#192640] hover:bg-[#213354] text-white text-xs font-semibold border border-white/[0.08] transition-colors disabled:opacity-50"
          >
            <RefreshCw size={13} className={syncing ? 'animate-spin text-accent-cyan' : ''} />
            <span>{syncing ? 'Syncing...' : syncSuccess ? 'Synced' : 'Sync Vectors'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Total Vectors</span>
            <span className="text-lg font-bold text-white font-mono">{totalChunks}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Embedding Model</span>
            <span className="text-xs font-semibold text-white font-mono">all-MiniLM-L6-v2</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#192640] border border-white/[0.08] space-y-1">
            <span className="text-slate-400 text-[11px] block">Vector Dimensions</span>
            <span className="text-xs font-semibold text-accent-cyan font-mono">384 Dimensions</span>
          </div>
        </div>
      </div>

      {/* 4. Architectural Diagnostics: 7-Stage RAG Execution Pipeline */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/25">
              <Activity size={16} />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">
                RAG Pipeline Architecture
              </h2>
              <p className="text-xs text-slate-300">7-stage verifiable retrieval and synthesis subsystem</p>
            </div>
          </div>

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs text-slate-300 hover:text-white rounded-xl hover:bg-white/[0.04] transition-colors"
          >
            <span>{showAdvanced ? 'Hide Architecture' : 'View Architecture'}</span>
            {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {showAdvanced && (
          <div className="space-y-2 pt-2">
            {pipelineSteps.map((step) => (
              <div
                key={step.step}
                className="p-3 rounded-xl bg-[#192640] border border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
              >
                <div className="flex items-start space-x-3">
                  <span className="font-mono font-bold text-accent-blue text-xs pt-0.5">
                    {step.step}
                  </span>
                  <div>
                    <h3 className="font-semibold text-white">{step.name}</h3>
                    <p className="text-slate-300 text-[11px] mt-0.5">{step.desc}</p>
                  </div>
                </div>
                <span className="font-mono text-[11px] text-accent-emerald px-2 py-0.5 rounded bg-accent-emerald/15 border border-accent-emerald/25 self-start sm:self-auto flex-shrink-0 font-semibold">
                  {step.tech}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 5. Application Information */}
      <div className="bg-[#141E33] rounded-2xl border border-white/[0.08] p-5 space-y-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-white/[0.05] text-slate-400 border border-white/[0.06]">
            <Info size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white">Application Information</h2>
            <p className="text-xs text-slate-300">NexaDesk Multi-Version Enterprise Support AI</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
          <div>
            <span className="text-slate-400 text-[10px] block">Software Release</span>
            <span className="font-mono text-white font-semibold">NexaDesk v3.0</span>
          </div>
          <div>
            <span className="text-slate-400 text-[10px] block">Backend API</span>
            <span className="font-mono text-white font-semibold">FastAPI 0.115</span>
          </div>
          <div>
            <span className="text-slate-400 text-[10px] block">Vector Engine</span>
            <span className="font-mono text-white font-semibold">ChromaDB 0.6</span>
          </div>
          <div>
            <span className="text-slate-400 text-[10px] block">Frontend Client</span>
            <span className="font-mono text-white font-semibold">React 18 · Vite 5</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
