'use client';

import React, { useState, useEffect, useRef } from 'react';
import { X, Download, FileJson, Activity, Loader2, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';

interface AgentAnalysis {
    score?: number;
    overall_score?: number;
    recommendation?: string;
    reasoning?: string;
    error?: string;
    [key: string]: any;
}

interface AnalysisResult {
    ticker: string;
    company_name?: string;
    current_price?: number;
    recommendation?: string;
    composite_score?: number;
    target_price?: number;
    confidence?: string;
    agent_analyses?: Record<string, AgentAnalysis>;
    predictor_analysis?: any;
    analysis_duration_seconds?: number;
    cached?: boolean;
    cache_age_seconds?: number;
    observability?: {
        total_cost_usd?: number;
        total_tokens?: number;
    };
    error?: string;
}

interface AIAnalysisModalProps {
    ticker: string | null;
    isOpen: boolean;
    onClose: () => void;
}

const AGENTS = [
    { key: 'fundamental_agent', name: 'Fundamental', emoji: '📈', color: 'blue' },
    { key: 'technical_agent', name: 'Technical', emoji: '📉', color: 'cyan' },
    { key: 'sentiment_agent', name: 'Sentiment', emoji: '📰', color: 'amber' },
    { key: 'macro_agent', name: 'Macro', emoji: '🌍', color: 'purple' },
    { key: 'regulatory_agent', name: 'Regulatory', emoji: '⚖️', color: 'emerald' },
];

const API_BASE = process.env.NEXT_PUBLIC_AGENT_API_URL || 'https://nifty-agents-api.onrender.com';

export default function AIAnalysisModal({ ticker, isOpen, onClose }: AIAnalysisModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [agentProgress, setAgentProgress] = useState<Record<string, 'idle' | 'running' | 'complete' | 'error'>>({});
    const modalRef = useRef<HTMLDivElement>(null);

    // Fetch analysis when modal opens with a ticker
    useEffect(() => {
        if (isOpen && ticker) {
            fetchAnalysis(ticker);
        }
    }, [isOpen, ticker]);

    // Reset state when modal closes
    useEffect(() => {
        if (!isOpen) {
            setResult(null);
            setError(null);
            setAgentProgress({});
        }
    }, [isOpen]);

    const fetchAnalysis = async (tickerSymbol: string) => {
        setLoading(true);
        setError(null);
        setResult(null);

        // Initialize agent progress
        const initialProgress: Record<string, 'idle' | 'running' | 'complete' | 'error'> = {};
        AGENTS.forEach(a => initialProgress[a.key] = 'running');
        setAgentProgress(initialProgress);

        try {
            const response = await fetch(`${API_BASE}/api/agent/analyze/${tickerSymbol}`);

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.status} ${response.statusText}`);
            }

            const data: AnalysisResult = await response.json();

            // Update agent progress based on results
            const finalProgress: Record<string, 'idle' | 'running' | 'complete' | 'error'> = {};
            AGENTS.forEach(a => {
                const analysis = data.agent_analyses?.[a.key];
                if (analysis?.error) {
                    finalProgress[a.key] = 'error';
                } else if (analysis) {
                    finalProgress[a.key] = 'complete';
                } else {
                    finalProgress[a.key] = 'idle';
                }
            });
            setAgentProgress(finalProgress);

            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Analysis failed');
            AGENTS.forEach(a => setAgentProgress(prev => ({ ...prev, [a.key]: 'error' })));
        } finally {
            setLoading(false);
        }
    };

    const handleExportJSON = () => {
        if (!result) return;
        const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${result.ticker}_analysis.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleExportPDF = () => {
        if (!result) return;
        // Create printable version and trigger print dialog
        const printContent = generatePrintableReport(result);
        const printWindow = window.open('', '_blank');
        if (printWindow) {
            printWindow.document.write(printContent);
            printWindow.document.close();
            printWindow.print();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div
                ref={modalRef}
                className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-slate-900 border border-slate-700 rounded-xl shadow-2xl m-4"
            >
                {/* Header */}
                <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-slate-800/95 backdrop-blur border-b border-slate-700">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Activity className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white">AI Agent Analysis</h2>
                            <p className="text-sm text-slate-400">
                                {ticker ? `Analyzing ${ticker}` : 'Multi-Agent Stock Intelligence'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        {result?.cached && (
                            <span className="px-2 py-1 text-xs bg-amber-500/20 text-amber-400 rounded border border-amber-500/30">
                                Cached ({Math.round((result.cache_age_seconds || 0) / 60)}m ago)
                            </span>
                        )}
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5 text-slate-400" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Loading State */}
                    {loading && (
                        <div className="text-center py-12">
                            <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
                            <p className="text-slate-400">Running AI agents in parallel...</p>
                            <p className="text-xs text-slate-500 mt-2">This may take 20-40 seconds</p>
                        </div>
                    )}

                    {/* Error State */}
                    {error && !loading && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-red-400 font-medium">Analysis Failed</p>
                                <p className="text-red-300/80 text-sm mt-1">{error}</p>
                                <button
                                    onClick={() => ticker && fetchAnalysis(ticker)}
                                    className="mt-3 flex items-center gap-2 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 rounded text-sm text-red-400 transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4" /> Retry
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Agent Progress */}
                    {(loading || result) && (
                        <div className="grid grid-cols-5 gap-3">
                            {AGENTS.map(agent => {
                                const status = agentProgress[agent.key] || 'idle';
                                const analysis = result?.agent_analyses?.[agent.key];
                                const score = analysis?.score || analysis?.overall_score;

                                return (
                                    <div
                                        key={agent.key}
                                        className={`
                      rounded-lg p-3 text-center border transition-all
                      ${status === 'running' ? 'bg-blue-500/10 border-blue-500/30 animate-pulse' : ''}
                      ${status === 'complete' ? 'bg-slate-800/50 border-slate-600' : ''}
                      ${status === 'error' ? 'bg-red-500/10 border-red-500/30' : ''}
                      ${status === 'idle' ? 'bg-slate-800/30 border-slate-700' : ''}
                    `}
                                    >
                                        <div className="text-2xl mb-1">{agent.emoji}</div>
                                        <div className="text-xs font-medium text-slate-300">{agent.name}</div>
                                        <div className="mt-2">
                                            {status === 'running' && (
                                                <span className="text-xs text-blue-400">Running...</span>
                                            )}
                                            {status === 'complete' && score && (
                                                <span className={`text-lg font-bold ${score >= 70 ? 'text-emerald-400' :
                                                        score >= 50 ? 'text-amber-400' : 'text-rose-400'
                                                    }`}>
                                                    {score.toFixed(0)}
                                                </span>
                                            )}
                                            {status === 'error' && (
                                                <span className="text-xs text-red-400">Error</span>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Results */}
                    {result && !loading && !error && (
                        <>
                            {/* Summary Cards */}
                            <div className="grid grid-cols-4 gap-4">
                                <div className="bg-slate-800/50 rounded-lg p-4 text-center border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">RECOMMENDATION</div>
                                    <div className={`text-xl font-bold ${result.recommendation?.toLowerCase() === 'buy' ? 'text-emerald-400' :
                                            result.recommendation?.toLowerCase() === 'sell' ? 'text-rose-400' : 'text-amber-400'
                                        }`}>
                                        {result.recommendation?.toUpperCase() || 'HOLD'}
                                    </div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4 text-center border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">COMPOSITE SCORE</div>
                                    <div className={`text-xl font-bold ${(result.composite_score || 0) >= 70 ? 'text-emerald-400' :
                                            (result.composite_score || 0) >= 50 ? 'text-amber-400' : 'text-rose-400'
                                        }`}>
                                        {result.composite_score?.toFixed(1) || '--'}
                                    </div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4 text-center border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">TARGET PRICE</div>
                                    <div className="text-xl font-bold text-cyan-400">
                                        {result.target_price ? `₹${result.target_price.toLocaleString()}` : '--'}
                                    </div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4 text-center border border-slate-700">
                                    <div className="text-xs text-slate-400 mb-1">CONFIDENCE</div>
                                    <div className="text-xl font-bold text-purple-400 capitalize">
                                        {result.confidence || '--'}
                                    </div>
                                </div>
                            </div>

                            {/* Duration & Cost */}
                            <div className="flex items-center justify-between text-xs text-slate-500 px-2">
                                <span>Analysis completed in {result.analysis_duration_seconds?.toFixed(1)}s</span>
                                <span>
                                    Cost: ${result.observability?.total_cost_usd?.toFixed(6) || '0.000000'} |
                                    Tokens: {result.observability?.total_tokens?.toLocaleString() || 0}
                                </span>
                            </div>

                            {/* Predictor Analysis */}
                            {result.predictor_analysis?.synthesis_reasoning && (
                                <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700">
                                    <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                                        AI Summary
                                    </h4>
                                    <p className="text-sm text-slate-400 leading-relaxed">
                                        {result.predictor_analysis.synthesis_reasoning}
                                    </p>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 flex items-center justify-between px-6 py-4 bg-slate-800/95 backdrop-blur border-t border-slate-700">
                    <div className="text-xs text-slate-500">
                        Powered by Gemini 2.0 Flash
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleExportJSON}
                            disabled={!result}
                            className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-slate-300 transition-colors"
                        >
                            <FileJson className="w-4 h-4" /> JSON
                        </button>
                        <button
                            onClick={handleExportPDF}
                            disabled={!result}
                            className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-slate-300 transition-colors"
                        >
                            <Download className="w-4 h-4" /> PDF
                        </button>
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium text-white transition-colors"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function generatePrintableReport(result: AnalysisResult): string {
    const agentRows = AGENTS.map(agent => {
        const analysis = result.agent_analyses?.[agent.key];
        const score = analysis?.score || analysis?.overall_score || '--';
        return `
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">${agent.emoji} ${agent.name}</td>
        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${score}</td>
        <td style="padding: 8px; border: 1px solid #ddd;">${analysis?.recommendation || '--'}</td>
      </tr>
    `;
    }).join('');

    return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${result.ticker} - AI Analysis Report</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
        h1 { color: #1e3a5f; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }
        .card { background: #f3f4f6; padding: 16px; border-radius: 8px; text-align: center; }
        .card-label { font-size: 12px; color: #6b7280; margin-bottom: 4px; }
        .card-value { font-size: 24px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin: 24px 0; }
        th { background: #1e3a5f; color: white; padding: 12px; text-align: left; }
        .timestamp { font-size: 12px; color: #9ca3af; margin-top: 32px; }
      </style>
    </head>
    <body>
      <h1>🤖 AI Analysis Report: ${result.ticker}</h1>
      <p><strong>${result.company_name || result.ticker}</strong> | Current Price: ₹${result.current_price?.toLocaleString() || '--'}</p>
      
      <div class="summary">
        <div class="card">
          <div class="card-label">RECOMMENDATION</div>
          <div class="card-value" style="color: ${result.recommendation?.toLowerCase() === 'buy' ? '#10b981' : result.recommendation?.toLowerCase() === 'sell' ? '#ef4444' : '#f59e0b'}">
            ${result.recommendation?.toUpperCase() || 'HOLD'}
          </div>
        </div>
        <div class="card">
          <div class="card-label">COMPOSITE SCORE</div>
          <div class="card-value" style="color: #3b82f6">${result.composite_score?.toFixed(1) || '--'}</div>
        </div>
        <div class="card">
          <div class="card-label">TARGET PRICE</div>
          <div class="card-value" style="color: #06b6d4">₹${result.target_price?.toLocaleString() || '--'}</div>
        </div>
        <div class="card">
          <div class="card-label">CONFIDENCE</div>
          <div class="card-value" style="color: #8b5cf6">${result.confidence || '--'}</div>
        </div>
      </div>

      <h2>Agent Scores</h2>
      <table>
        <thead>
          <tr>
            <th>Agent</th>
            <th>Score</th>
            <th>Signal</th>
          </tr>
        </thead>
        <tbody>
          ${agentRows}
        </tbody>
      </table>

      ${result.predictor_analysis?.synthesis_reasoning ? `
        <h2>AI Summary</h2>
        <p>${result.predictor_analysis.synthesis_reasoning}</p>
      ` : ''}

      <p class="timestamp">Generated: ${new Date().toLocaleString()} | Analysis Duration: ${result.analysis_duration_seconds?.toFixed(1)}s</p>
    </body>
    </html>
  `;
}
