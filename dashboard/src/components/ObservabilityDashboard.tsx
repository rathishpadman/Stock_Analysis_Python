'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, DollarSign, Clock, AlertTriangle, 
  ChevronDown, ChevronRight, RefreshCw, Search,
  Cpu, MessageSquare, TrendingUp, Zap, Eye,
  FileText, Filter, Download
} from 'lucide-react';

// Types
interface AgentLog {
  timestamp: string;
  trace_id: string;
  span_id: string;
  ticker: string;
  agent_name: string;
  event_type: string;
  duration_ms?: number;
  status: string;
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: number;
  error_message?: string;
  reasoning?: string;
  llm_request?: {
    system_prompt: string;
    user_prompt: string;
    model: string;
    temperature: number;
  };
  llm_response?: {
    raw_response: string;
    parsed_response: any;
    input_tokens?: number;
    output_tokens?: number;
    latency_ms?: number;
  };
}

interface FinOpsEntry {
  timestamp: string;
  trace_id: string;
  ticker: string;
  model: string;
  agent_name: string;
  input_tokens: number;
  output_tokens: number;
  total_cost_usd: number;
}

interface Metrics {
  total_analyses: number;
  successful_analyses: number;
  failed_analyses: number;
  total_cost_usd: number;
  total_input_tokens: number;
  total_output_tokens: number;
  costs_by_date: Record<string, number>;
}

interface ModelInfo {
  current_model: string;
  current_cost_per_analysis_usd: number;
  tokens_per_analysis: {
    input: number;
    output: number;
    total: number;
  };
  available_models: Record<string, any>;
}

// Agent API base URL - configurable
const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8000';

export default function ObservabilityDashboard() {
  // State
  const [activeTab, setActiveTab] = useState<'overview' | 'logs' | 'traces' | 'finops'>('overview');
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [finops, setFinops] = useState<FinOpsEntry[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTrace, setExpandedTrace] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAgent, setFilterAgent] = useState<string>('all');
  const [filterEventType, setFilterEventType] = useState<string>('all');

  // Fetch data
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [logsRes, finopsRes, metricsRes, modelsRes] = await Promise.all([
        fetch(`${AGENT_API_URL}/api/agent/observability/logs?n=100`),
        fetch(`${AGENT_API_URL}/api/agent/observability/finops?n=100`),
        fetch(`${AGENT_API_URL}/api/agent/observability/metrics`),
        fetch(`${AGENT_API_URL}/api/agent/observability/models`)
      ]);

      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData.logs || []);
      }
      
      if (finopsRes.ok) {
        const finopsData = await finopsRes.json();
        setFinops(finopsData.entries || []);
      }
      
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData.metrics || null);
      }
      
      if (modelsRes.ok) {
        const modelsData = await modelsRes.json();
        setModelInfo(modelsData || null);
      }
    } catch (err) {
      setError('Failed to connect to Agent API. Make sure it\'s running on ' + AGENT_API_URL);
      console.error('Observability fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter logs
  const filteredLogs = logs.filter(log => {
    const matchesSearch = !searchQuery || 
      log.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.trace_id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAgent = filterAgent === 'all' || log.agent_name === filterAgent;
    const matchesEvent = filterEventType === 'all' || log.event_type === filterEventType;
    return matchesSearch && matchesAgent && matchesEvent;
  });

  // Get unique agents and event types for filters
  const uniqueAgents = [...new Set(logs.map(l => l.agent_name).filter(Boolean))];
  const uniqueEventTypes = [...new Set(logs.map(l => l.event_type).filter(Boolean))];

  // Calculate daily costs for chart
  const dailyCosts = metrics?.costs_by_date || {};
  const sortedDates = Object.keys(dailyCosts).sort().slice(-7);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-slate-400">Loading observability data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-500" />
          <div>
            <h3 className="text-red-400 font-semibold">Connection Error</h3>
            <p className="text-slate-400 text-sm mt-1">{error}</p>
            <button 
              onClick={fetchAllData}
              className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm"
            >
              Retry Connection
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-500" />
            AI Agent Observability
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            Monitor agent executions, LLM traces, and API costs
          </p>
        </div>
        <button 
          onClick={fetchAllData}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700 pb-2">
        {[
          { id: 'overview', label: 'Overview', icon: TrendingUp },
          { id: 'logs', label: 'Agent Logs', icon: FileText },
          { id: 'traces', label: 'LLM Traces', icon: MessageSquare },
          { id: 'finops', label: 'FinOps', icon: DollarSign }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-t text-sm font-medium flex items-center gap-2 transition-colors ${
              activeTab === tab.id 
                ? 'bg-slate-800 text-white border-b-2 border-purple-500' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard 
              title="Total Analyses"
              value={metrics?.total_analyses || 0}
              icon={Cpu}
              color="blue"
            />
            <StatCard 
              title="Success Rate"
              value={metrics ? `${((metrics.successful_analyses / Math.max(metrics.total_analyses, 1)) * 100).toFixed(1)}%` : '0%'}
              icon={Zap}
              color="green"
            />
            <StatCard 
              title="Total Cost"
              value={`$${(metrics?.total_cost_usd || 0).toFixed(4)}`}
              icon={DollarSign}
              color="amber"
            />
            <StatCard 
              title="Total Tokens"
              value={((metrics?.total_input_tokens || 0) + (metrics?.total_output_tokens || 0)).toLocaleString()}
              icon={MessageSquare}
              color="purple"
            />
          </div>

          {/* Model Info */}
          {modelInfo && (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <Cpu className="w-4 h-4" />
                Current Model Configuration
              </h3>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Model:</span>
                  <span className="ml-2 text-white font-mono">{modelInfo.current_model}</span>
                </div>
                <div>
                  <span className="text-slate-500">Cost/Analysis:</span>
                  <span className="ml-2 text-green-400">${modelInfo.current_cost_per_analysis_usd?.toFixed(6)}</span>
                </div>
                <div>
                  <span className="text-slate-500">Input Tokens:</span>
                  <span className="ml-2 text-white">~{modelInfo.tokens_per_analysis?.input?.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-slate-500">Output Tokens:</span>
                  <span className="ml-2 text-white">~{modelInfo.tokens_per_analysis?.output?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Daily Cost Chart */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Daily Costs (Last 7 Days)</h3>
            <div className="flex items-end gap-2 h-32">
              {sortedDates.map(date => {
                const cost = dailyCosts[date] || 0;
                const maxCost = Math.max(...Object.values(dailyCosts), 0.001);
                const height = (cost / maxCost) * 100;
                return (
                  <div key={date} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-purple-500/50 rounded-t hover:bg-purple-500/70 transition-colors"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`$${cost.toFixed(6)}`}
                    />
                    <span className="text-[10px] text-slate-500 mt-1">{date.slice(5)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">Recent Activity</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {logs.slice(0, 10).map((log, idx) => (
                <div key={idx} className="flex items-center gap-3 text-sm py-2 border-b border-slate-700/50">
                  <span className={`w-2 h-2 rounded-full ${log.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-slate-400 w-20 font-mono text-xs">{log.timestamp?.slice(11, 19)}</span>
                  <span className="text-white font-medium w-24">{log.ticker}</span>
                  <span className="text-purple-400 w-32">{log.agent_name}</span>
                  <span className="text-slate-500 flex-1">{log.event_type}</span>
                  {log.duration_ms && <span className="text-slate-400">{log.duration_ms.toFixed(0)}ms</span>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search by ticker or trace ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm"
              />
            </div>
            <select
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm"
            >
              <option value="all">All Agents</option>
              {uniqueAgents.map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </select>
            <select
              value={filterEventType}
              onChange={(e) => setFilterEventType(e.target.value)}
              className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm"
            >
              <option value="all">All Events</option>
              {uniqueEventTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          {/* Logs Table */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-900/50">
                <tr>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Ticker</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Agent</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Event</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Duration</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map((log, idx) => (
                  <tr 
                    key={idx} 
                    className="border-t border-slate-700/50 hover:bg-slate-700/30 cursor-pointer"
                    onClick={() => setExpandedTrace(expandedTrace === log.trace_id ? null : log.trace_id)}
                  >
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">{log.timestamp?.slice(11, 19)}</td>
                    <td className="px-4 py-3 text-white font-medium">{log.ticker}</td>
                    <td className="px-4 py-3 text-purple-400">{log.agent_name}</td>
                    <td className="px-4 py-3 text-slate-300">{log.event_type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        log.status === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{log.duration_ms?.toFixed(0)}ms</td>
                    <td className="px-4 py-3 text-slate-400">
                      {log.input_tokens && log.output_tokens 
                        ? `${log.input_tokens}/${log.output_tokens}` 
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* LLM Traces Tab */}
      {activeTab === 'traces' && (
        <div className="space-y-4">
          <p className="text-slate-400 text-sm">
            View detailed LLM request/response pairs. Click to expand and see full prompts and responses.
          </p>
          
          {logs.filter(l => l.event_type === 'llm_response' || l.event_type === 'llm_request').map((log, idx) => (
            <div key={idx} className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
              <div 
                className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-slate-700/30"
                onClick={() => setExpandedTrace(expandedTrace === `${log.trace_id}-${idx}` ? null : `${log.trace_id}-${idx}`)}
              >
                <div className="flex items-center gap-4">
                  {expandedTrace === `${log.trace_id}-${idx}` ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  <span className="text-white font-medium">{log.ticker}</span>
                  <span className="text-purple-400">{log.agent_name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    log.event_type === 'llm_request' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                  }`}>
                    {log.event_type}
                  </span>
                </div>
                <span className="text-slate-500 text-sm font-mono">{log.timestamp?.slice(11, 19)}</span>
              </div>
              
              {expandedTrace === `${log.trace_id}-${idx}` && (
                <div className="border-t border-slate-700 p-4 space-y-4">
                  {log.llm_request && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2">System Prompt</h4>
                      <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-x-auto max-h-40 overflow-y-auto">
                        {log.llm_request.system_prompt}
                      </pre>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2 mt-4">User Prompt</h4>
                      <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-x-auto max-h-60 overflow-y-auto">
                        {log.llm_request.user_prompt}
                      </pre>
                    </div>
                  )}
                  
                  {log.llm_response && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2">Raw Response</h4>
                      <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-x-auto max-h-60 overflow-y-auto">
                        {log.llm_response.raw_response}
                      </pre>
                      {log.llm_response.parsed_response && (
                        <>
                          <h4 className="text-sm font-semibold text-slate-300 mb-2 mt-4">Parsed Response</h4>
                          <pre className="bg-slate-900 p-3 rounded text-xs text-green-300 overflow-x-auto max-h-60 overflow-y-auto">
                            {JSON.stringify(log.llm_response.parsed_response, null, 2)}
                          </pre>
                        </>
                      )}
                      <div className="flex gap-4 mt-3 text-xs text-slate-500">
                        <span>Latency: {log.llm_response.latency_ms?.toFixed(0)}ms</span>
                        <span>Input: {log.llm_response.input_tokens} tokens</span>
                        <span>Output: {log.llm_response.output_tokens} tokens</span>
                      </div>
                    </div>
                  )}
                  
                  {log.reasoning && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-300 mb-2">Agent Reasoning</h4>
                      <p className="bg-slate-900 p-3 rounded text-xs text-amber-300">{log.reasoning}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          
          {logs.filter(l => l.event_type === 'llm_response' || l.event_type === 'llm_request').length === 0 && (
            <div className="text-center py-12 text-slate-500">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No LLM traces found. Run an agent analysis to see traces.</p>
            </div>
          )}
        </div>
      )}

      {/* FinOps Tab */}
      {activeTab === 'finops' && (
        <div className="space-y-6">
          {/* Cost Summary Cards */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard 
              title="Today's Cost"
              value={`$${(dailyCosts[new Date().toISOString().slice(0, 10)] || 0).toFixed(6)}`}
              icon={DollarSign}
              color="green"
            />
            <StatCard 
              title="This Week"
              value={`$${sortedDates.reduce((sum, d) => sum + (dailyCosts[d] || 0), 0).toFixed(4)}`}
              icon={TrendingUp}
              color="blue"
            />
            <StatCard 
              title="Avg Cost/Analysis"
              value={`$${(metrics ? metrics.total_cost_usd / Math.max(metrics.total_analyses, 1) : 0).toFixed(6)}`}
              icon={Activity}
              color="purple"
            />
            <StatCard 
              title="Total Lifetime"
              value={`$${(metrics?.total_cost_usd || 0).toFixed(4)}`}
              icon={DollarSign}
              color="amber"
            />
          </div>

          {/* Cost Breakdown Table */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700">
              <h3 className="text-sm font-semibold text-slate-300">Cost Breakdown by API Call</h3>
            </div>
            <table className="w-full text-sm">
              <thead className="bg-slate-900/50">
                <tr>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Ticker</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Agent</th>
                  <th className="px-4 py-3 text-left text-slate-400 font-medium">Model</th>
                  <th className="px-4 py-3 text-right text-slate-400 font-medium">Input Tokens</th>
                  <th className="px-4 py-3 text-right text-slate-400 font-medium">Output Tokens</th>
                  <th className="px-4 py-3 text-right text-slate-400 font-medium">Cost</th>
                </tr>
              </thead>
              <tbody>
                {finops.slice(0, 50).map((entry, idx) => (
                  <tr key={idx} className="border-t border-slate-700/50 hover:bg-slate-700/30">
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">{entry.timestamp?.slice(11, 19)}</td>
                    <td className="px-4 py-3 text-white font-medium">{entry.ticker}</td>
                    <td className="px-4 py-3 text-purple-400">{entry.agent_name}</td>
                    <td className="px-4 py-3 text-slate-300 font-mono text-xs">{entry.model}</td>
                    <td className="px-4 py-3 text-right text-slate-400">{entry.input_tokens?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-slate-400">{entry.output_tokens?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-green-400">${entry.total_cost_usd?.toFixed(6)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Model Pricing Reference */}
          {modelInfo?.available_models && (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-700">
                <h3 className="text-sm font-semibold text-slate-300">Available Models & Pricing</h3>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-slate-400 font-medium">Model</th>
                    <th className="px-4 py-3 text-right text-slate-400 font-medium">Cost/Analysis</th>
                    <th className="px-4 py-3 text-left text-slate-400 font-medium">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(modelInfo.available_models).map(([name, info]: [string, any]) => (
                    <tr key={name} className={`border-t border-slate-700/50 ${name === modelInfo.current_model ? 'bg-purple-500/10' : ''}`}>
                      <td className="px-4 py-3 font-mono text-white">
                        {name}
                        {name === modelInfo.current_model && (
                          <span className="ml-2 text-xs bg-purple-500 text-white px-2 py-0.5 rounded">ACTIVE</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-green-400">${info.cost_per_analysis?.toFixed(6)}</td>
                      <td className="px-4 py-3 text-slate-400 text-xs">{info.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Stat Card Component
function StatCard({ title, value, icon: Icon, color }: { title: string; value: string | number; icon: any; color: string }) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
    amber: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400'
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-400">{title}</span>
        <Icon className="w-5 h-5 opacity-50" />
      </div>
      <div className="text-2xl font-bold mt-2">{value}</div>
    </div>
  );
}
