import React from 'react';
import { BarChart3, Target, Award, Cpu, AlertCircle, FileCheck } from 'lucide-react';

export function AnalyticsView() {
  const metrics = [
    {
      title: 'Context Relevance',
      description: 'Fraction of retrieved chunks strictly relevant to query',
      target: '> 0.85',
      phase: 'Phase 3 Evaluation',
      icon: <Target className="w-5 h-5 text-indigo-600" />,
    },
    {
      title: 'Groundedness / Faithfulness',
      description: 'Degree to which generated answers stay truthful to source',
      target: '> 0.90',
      phase: 'Phase 3 Evaluation',
      icon: <FileCheck className="w-5 h-5 text-emerald-600" />,
    },
    {
      title: 'Version Disambiguation',
      description: 'Accuracy in preventing cross-version hallucinations (v1 vs v2 vs v3)',
      target: '> 0.95',
      phase: 'Phase 3 Evaluation',
      icon: <Award className="w-5 h-5 text-purple-600" />,
    },
    {
      title: 'Retrieval Latency (p95)',
      description: 'ChromaDB dense search + BM25 hybrid ranking speed',
      target: '< 350 ms',
      phase: 'Phase 3 Evaluation',
      icon: <Cpu className="w-5 h-5 text-amber-600" />,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center space-x-3 mb-2">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          <h2 className="text-lg font-bold text-slate-900">RAG Triad & Benchmark Analytics</h2>
        </div>
        <p className="text-xs text-slate-500">
          Academic and experimental evaluation metrics tracking retrieval quality and version isolation across NexaDesk releases.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((m) => (
          <div key={m.title} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                {m.icon}
                <h4 className="font-semibold text-sm text-slate-800">{m.title}</h4>
              </div>
              <span className="text-[11px] font-semibold font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Target: {m.target}
              </span>
            </div>
            <p className="text-xs text-slate-600 mb-3">{m.description}</p>
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-100">
              <span>Harness: scripts/run_evaluation.py</span>
              <span className="text-indigo-600 font-medium">{m.phase}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AnalyticsView;

