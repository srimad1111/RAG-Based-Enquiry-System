import React from 'react';
import { Layers, Database, Cpu, Sparkles } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            <p className="font-semibold text-slate-700">
              Project 32: RAG-Based Customer Enquiry System over Company Documentation
            </p>
            <p className="mt-0.5">Final-Year AI/ML Capstone Project | NexaDesk Case Study</p>
          </div>

          <div className="flex items-center flex-wrap gap-3">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
              <Cpu size={12} /> FastAPI
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
              <Database size={12} /> ChromaDB + SQLite
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
              <Layers size={12} /> LangChain + BM25
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
              <Sparkles size={12} /> Gemini API
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

