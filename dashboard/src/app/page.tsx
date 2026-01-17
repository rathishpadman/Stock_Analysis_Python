'use client';

import React, { useState, useEffect, useMemo } from 'react';
import WeeklyReportTableV2 from '@/components/WeeklyReportTableV2';
import MonthlyReportTableV2 from '@/components/MonthlyReportTableV2';
import SeasonalityHeatmapV2 from '@/components/SeasonalityHeatmapV2';
import TopMovers from '@/components/TopMovers';
import TechnicalSignals from '@/components/TechnicalSignals';
import { WeeklyPriceChart, WeeklyRSIChart, WeeklyReturnsChart, WeeklyVolumeChart, WeeklyStats } from '@/components/WeeklyCharts';
import { MonthlyPriceChart, MonthlyReturnsChart, RollingReturnsChart, MonthlyVolumeChart, MonthlyStats } from '@/components/MonthlyCharts';
import { SeasonalityBarChart, SeasonalityRadarChart, QuarterlyBreakdown, SeasonalityStats } from '@/components/SeasonalityCharts';
import { ScoreBarChart, PriceChart, RSIChart, MACDChart } from '@/components/Charts';
import { ALL_FIELDS, DEFAULT_COLUMNS, WEEKLY_FIELDS, DEFAULT_WEEKLY_COLUMNS, MONTHLY_FIELDS, DEFAULT_MONTHLY_COLUMNS, SEASONALITY_FIELDS, DEFAULT_SEASONALITY_COLUMNS } from '@/lib/constants';
import { Settings2, Search, Filter, LogOut, Loader2, BarChart3, TrendingUp, ShieldCheck, Info, Calendar, Flame, AlertTriangle, Activity, ChevronLeft } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import StockTable from '@/components/StockTable';

type ReportView = 'daily' | 'weekly' | 'monthly' | 'seasonality';
type DetailSource = 'daily' | 'weekly' | 'monthly' | 'seasonality';

export default function DashboardPage() {
  const { user, loading: authLoading, signInWithGoogle, signOut } = useAuth();
  
  // Data states
  const [stocks, setStocks] = useState<any[]>([]);
  const [weeklyData, setWeeklyData] = useState<any[]>([]);
  const [monthlyData, setMonthlyData] = useState<any[]>([]);
  const [seasonalityData, setSeasonalityData] = useState<any[]>([]);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [weeklyHistoricalData, setWeeklyHistoricalData] = useState<any[]>([]);
  const [monthlyHistoricalData, setMonthlyHistoricalData] = useState<any[]>([]);
  const [seasonalityDetailData, setSeasonalityDetailData] = useState<any>(null);
  
  // UI states
  const [loading, setLoading] = useState(true);
  const [chartsLoading, setChartsLoading] = useState(false);
  const [timeframe, setTimeframe] = useState<'1d' | '1w' | '1m'>('1d');
  const [visibleColumns, setVisibleColumns] = useState(DEFAULT_COLUMNS);
  const [weeklyVisibleColumns, setWeeklyVisibleColumns] = useState(DEFAULT_WEEKLY_COLUMNS);
  const [monthlyVisibleColumns, setMonthlyVisibleColumns] = useState(DEFAULT_MONTHLY_COLUMNS);
  const [seasonalityVisibleColumns, setSeasonalityVisibleColumns] = useState(DEFAULT_SEASONALITY_COLUMNS);
  const [searchQuery, setSearchQuery] = useState('');
  const [showColumnPicker, setShowColumnPicker] = useState(false);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [view, setView] = useState<'table' | 'detail'>('table');
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [reportView, setReportView] = useState<ReportView>('daily');
  const [detailSource, setDetailSource] = useState<DetailSource>('daily');

  // Get current fields and columns based on reportView
  const currentFields = useMemo(() => {
    switch (reportView) {
      case 'weekly': return WEEKLY_FIELDS;
      case 'monthly': return MONTHLY_FIELDS;
      case 'seasonality': return SEASONALITY_FIELDS;
      default: return ALL_FIELDS;
    }
  }, [reportView]);

  const currentVisibleColumns = useMemo(() => {
    switch (reportView) {
      case 'weekly': return weeklyVisibleColumns;
      case 'monthly': return monthlyVisibleColumns;
      case 'seasonality': return seasonalityVisibleColumns;
      default: return visibleColumns;
    }
  }, [reportView, visibleColumns, weeklyVisibleColumns, monthlyVisibleColumns, seasonalityVisibleColumns]);

  const toggleCurrentColumn = (columnId: string) => {
    switch (reportView) {
      case 'weekly':
        setWeeklyVisibleColumns(prev => 
          prev.includes(columnId) ? prev.filter(c => c !== columnId) : [...prev, columnId]
        );
        break;
      case 'monthly':
        setMonthlyVisibleColumns(prev => 
          prev.includes(columnId) ? prev.filter(c => c !== columnId) : [...prev, columnId]
        );
        break;
      case 'seasonality':
        setSeasonalityVisibleColumns(prev => 
          prev.includes(columnId) ? prev.filter(c => c !== columnId) : [...prev, columnId]
        );
        break;
      default:
        setVisibleColumns(prev => 
          prev.includes(columnId) ? prev.filter(c => c !== columnId) : [...prev, columnId]
        );
    }
  };

  useEffect(() => {
    if (!authLoading && user) {
      fetchAvailableDates();
    }
  }, [user, authLoading]);

  useEffect(() => {
    if (!authLoading && user) {
      fetchStocks(selectedDate);
    }
  }, [user, authLoading, selectedDate]);

  useEffect(() => {
    if (selectedStock) {
      if (detailSource === 'daily') {
        fetchHistoricalData(selectedStock);
      } else if (detailSource === 'weekly') {
        fetchWeeklyHistoricalData(selectedStock);
      } else if (detailSource === 'monthly') {
        fetchMonthlyHistoricalData(selectedStock);
      } else if (detailSource === 'seasonality') {
        fetchSeasonalityDetailData(selectedStock);
      }
    }
  }, [selectedStock, detailSource]);

  // Fetch Weekly Data when view changes
  useEffect(() => {
    if (reportView === 'weekly' && weeklyData.length === 0) {
      fetchWeeklyData();
    }
    if (reportView === 'monthly' && monthlyData.length === 0) {
      fetchMonthlyData();
    }
    if (reportView === 'seasonality' && seasonalityData.length === 0) {
      fetchSeasonalityData();
    }
  }, [reportView]);

  const fetchWeeklyData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/weekly?limit=200');
      const data = await res.json();
      setWeeklyData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch weekly reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMonthlyData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/monthly?limit=200');
      const data = await res.json();
      setMonthlyData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch monthly reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSeasonalityData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/seasonality');
      const data = await res.json();
      setSeasonalityData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch seasonality data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableDates = async () => {
    try {
      const { data, error } = await supabase
        .from('daily_stocks')
        .select('date')
        .order('date', { ascending: false });

      if (data) {
        const uniqueDates = Array.from(new Set(data.map((d: any) => d.date))) as string[];
        setAvailableDates(uniqueDates);
        if (uniqueDates.length > 0 && !selectedDate) {
          setSelectedDate(uniqueDates[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch dates:', error);
    }
  };

  const fetchStocks = async (date?: string) => {
    setLoading(true);
    try {
      const url = date ? `/api/stocks?date=${date}` : '/api/stocks';
      const res = await fetch(url);
      const data = await res.json();
      setStocks(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async (ticker: string) => {
    setChartsLoading(true);
    try {
      const res = await fetch(`/api/stocks/${ticker}`);
      const data = await res.json();
      setHistoricalData(data);
    } catch (error) {
      console.error('Failed to fetch historical data:', error);
    } finally {
      setChartsLoading(false);
    }
  };

  const fetchWeeklyHistoricalData = async (ticker: string) => {
    setChartsLoading(true);
    try {
      const res = await fetch(`/api/weekly/${ticker}?weeks=52`);
      const data = await res.json();
      setWeeklyHistoricalData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch weekly historical data:', error);
    } finally {
      setChartsLoading(false);
    }
  };

  const fetchMonthlyHistoricalData = async (ticker: string) => {
    setChartsLoading(true);
    try {
      const res = await fetch(`/api/monthly/${ticker}?months=24`);
      const data = await res.json();
      setMonthlyHistoricalData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch monthly historical data:', error);
    } finally {
      setChartsLoading(false);
    }
  };

  const fetchSeasonalityDetailData = async (ticker: string) => {
    setChartsLoading(true);
    try {
      const res = await fetch(`/api/seasonality/${ticker}`);
      const data = await res.json();
      setSeasonalityDetailData(data);
    } catch (error) {
      console.error('Failed to fetch seasonality data:', error);
    } finally {
      setChartsLoading(false);
    }
  };

  const toggleColumn = (id: string) => {
    setVisibleColumns(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  // Context-aware search filter
  const getFilteredData = useMemo(() => {
    const query = searchQuery.toLowerCase();
    
    switch (reportView) {
      case 'daily':
        return stocks.filter(s =>
          s.ticker?.toLowerCase().includes(query) ||
          s.company_name?.toLowerCase().includes(query) ||
          s.sector?.toLowerCase().includes(query)
        );
      case 'weekly':
        return weeklyData.filter(s =>
          s.ticker?.toLowerCase().includes(query) ||
          s.company_name?.toLowerCase().includes(query)
        );
      case 'monthly':
        return monthlyData.filter(s =>
          s.ticker?.toLowerCase().includes(query) ||
          s.company_name?.toLowerCase().includes(query)
        );
      case 'seasonality':
        return seasonalityData.filter(s =>
          s.ticker?.toLowerCase().includes(query) ||
          s.company_name?.toLowerCase().includes(query)
        );
      default:
        return [];
    }
  }, [reportView, searchQuery, stocks, weeklyData, monthlyData, seasonalityData]);

  // Sidebar data based on current view
  const sidebarData = useMemo(() => {
    switch (reportView) {
      case 'daily':
        return stocks;
      case 'weekly':
        return weeklyData;
      case 'monthly':
        return monthlyData;
      case 'seasonality':
        return seasonalityData;
      default:
        return [];
    }
  }, [reportView, stocks, weeklyData, monthlyData, seasonalityData]);

  const filteredSidebar = sidebarData.filter(s =>
    s.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleStockSelect = (ticker: string, source: DetailSource = 'daily') => {
    setSelectedStock(ticker);
    setDetailSource(source);
    setView('detail');
  };

  if (authLoading) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-10 w-10 text-blue-600 animate-spin mx-auto mb-4" />
        <p className="text-slate-500 font-medium">Authenticating...</p>
      </div>
    </div>
  );

  if (!user) return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full text-center space-y-8 bg-slate-900 border border-slate-800 p-12 rounded-2xl shadow-2xl">
        <h1 className="text-4xl font-extrabold text-white tracking-tight">Antigravity Terminal</h1>
        <p className="text-slate-400">Professional Grade Stock Analysis Engine.</p>
        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-3 bg-white text-black font-bold py-3 px-6 rounded-lg hover:bg-slate-200 transition-all shadow-lg text-lg"
        >
          <svg className="h-5 w-5" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 12-4.53z" fill="#EA4335" />
          </svg>
          Enter Terminal
        </button>
      </div>
    </div>
  );

  const selectedStockData = stocks.find(s => s.ticker === selectedStock);
  const selectedWeeklyStockData = weeklyData.find(s => s.ticker === selectedStock);
  const selectedMonthlyStockData = monthlyData.find(s => s.ticker === selectedStock);
  const selectedSeasonalityStockData = seasonalityData.find(s => s.ticker === selectedStock);

  return (
    <div className="min-h-screen bg-[#05080f] text-slate-100 flex flex-col">
      <header className="border-b border-white/5 bg-[#0a0f1a]/80 backdrop-blur-md sticky top-0 z-40 p-4 flex items-center justify-between shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tighter text-white uppercase italic">Antigravity Terminal</h1>
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              LIVE DATA STREAMING
              <span className="ml-2 border-l border-slate-800 pl-2">V1.3.0-PHASE5_REPORTING</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Date selector - only for daily view */}
          {reportView === 'daily' && (
            <div className="flex items-center gap-2 bg-[#0f172a] border border-white/5 rounded px-3 py-1.5">
              <Calendar className="h-3 w-3 text-blue-500" />
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="bg-transparent text-[10px] font-mono text-slate-300 focus:outline-none cursor-pointer uppercase"
              >
                {availableDates.map(date => (
                  <option key={date} value={date} className="bg-slate-900">{date}</option>
                ))}
              </select>
            </div>
          )}

          {/* Context-aware search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-600" />
            <input
              type="text"
              placeholder={`Search ${reportView.toUpperCase()}...`}
              className="bg-[#0f172a] border border-white/5 rounded pl-10 pr-4 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all w-64 text-slate-300 font-mono"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <button
            onClick={() => setShowColumnPicker(!showColumnPicker)}
            className={`p-2 rounded border border-white/5 transition-all ${showColumnPicker ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-slate-900 text-slate-500 hover:text-slate-300'}`}
          >
            <Settings2 className="h-4 w-4" />
          </button>

          <button
            onClick={signOut}
            className="p-2 bg-rose-950/20 hover:bg-rose-900/40 border border-rose-900/30 rounded text-rose-500 transition-all"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Market List */}
        <aside className="w-[400px] border-r border-white/5 overflow-y-auto flex flex-col bg-[#070b14]">
          <div className="p-4 border-b border-white/5 flex items-center justify-between sticky top-0 bg-[#070b14] z-10">
            <h2 className="text-xs font-bold text-slate-500 flex items-center gap-2">
              <BarChart3 className="h-3 w-3" />
              {reportView.toUpperCase()} UNIVERSE ({filteredSidebar.length})
            </h2>
            <div className="flex gap-1">
              <button onClick={() => setView('table')} className={`p-1.5 rounded text-[10px] font-bold ${view === 'table' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-800'}`}>GRID</button>
              <button onClick={() => setView('detail')} className={`p-1.5 rounded text-[10px] font-bold ${view === 'detail' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-800'}`}>DETAIL</button>
            </div>
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-600 italic text-xs">Loading data...</div>
          ) : (
            <div className="divide-y divide-white/[0.03]">
              {filteredSidebar.slice(0, 100).map(stock => {
                const returnField = reportView === 'daily' ? stock.return_1d :
                                   reportView === 'weekly' ? stock.weekly_return_pct :
                                   reportView === 'monthly' ? stock.monthly_return_pct : null;
                const priceField = reportView === 'daily' ? stock.price_last :
                                  reportView === 'weekly' ? stock.weekly_close :
                                  reportView === 'monthly' ? stock.monthly_close : null;
                
                return (
                  <div
                    key={stock.ticker}
                    onClick={() => handleStockSelect(stock.ticker, reportView === 'weekly' ? 'weekly' : 'daily')}
                    className={`p-4 cursor-pointer transition-all hover:bg-blue-600/5 group relative ${selectedStock === stock.ticker ? 'bg-blue-600/10 border-l-2 border-l-blue-500' : ''}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-sm tracking-tight group-hover:text-blue-400 transition-colors uppercase italic">{stock.ticker}</span>
                      {returnField !== null && (
                        <span className={`text-[10px] font-mono ${(returnField || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                          {(returnField || 0) >= 0 ? '▲' : '▼'}{Math.abs(returnField || 0).toFixed(2)}%
                        </span>
                      )}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] text-slate-600 truncate max-w-[150px] uppercase">{stock.company_name}</span>
                      {priceField && <span className="text-[10px] font-bold text-slate-400">₹{priceField?.toLocaleString()}</span>}
                    </div>
                    {reportView === 'daily' && stock.overall_score && (
                      <div className="mt-2 flex gap-2">
                        <div className="h-1 flex-1 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${(stock.overall_score || 0) > 70 ? 'bg-emerald-500' : (stock.overall_score || 0) > 40 ? 'bg-amber-500' : 'bg-rose-500'}`}
                            style={{ width: `${stock.overall_score || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-[9px] font-bold text-slate-500">{stock.overall_score?.toFixed(0)}</span>
                      </div>
                    )}
                    {reportView === 'weekly' && stock.weekly_trend && (
                      <div className="mt-2">
                        <span className={`text-[9px] px-2 py-0.5 rounded ${
                          stock.weekly_trend === 'UP' ? 'bg-green-500/20 text-green-400' :
                          stock.weekly_trend === 'DOWN' ? 'bg-red-500/20 text-red-400' :
                          'bg-slate-700 text-slate-400'
                        }`}>
                          {stock.weekly_trend}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </aside>

        {/* Main Analysis Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#05080f] relative">
          {view === 'table' ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <h2 className="text-xl font-bold flex items-center gap-2">
                    <div className="w-1 h-6 bg-blue-600 rounded-full"></div>
                    {reportView === 'daily' ? 'DAILY SCREENER' : 
                     reportView === 'weekly' ? 'WEEKLY INTELLIGENCE' : 
                     reportView === 'monthly' ? 'MONTHLY ANALYSIS' : 'SEASONALITY PATTERNS'}
                  </h2>
                  <div className="flex bg-[#0f172a] border border-white/5 rounded p-0.5">
                    <button
                      onClick={() => setReportView('daily')}
                      className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${reportView === 'daily' ? 'bg-blue-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      DAILY
                    </button>
                    <button
                      onClick={() => setReportView('weekly')}
                      className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${reportView === 'weekly' ? 'bg-blue-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      WEEKLY
                    </button>
                    <button
                      onClick={() => setReportView('monthly')}
                      className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${reportView === 'monthly' ? 'bg-blue-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      MONTHLY
                    </button>
                    <button
                      onClick={() => setReportView('seasonality')}
                      className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${reportView === 'seasonality' ? 'bg-amber-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                      SEASONALITY
                    </button>
                  </div>
                </div>

                {reportView === 'daily' && (
                  <div className="flex gap-4">
                    <div className="flex bg-[#0f172a] border border-white/5 rounded p-1">
                      {(['1d', '1w', '1m'] as const).map((tf) => (
                        <button
                          key={tf}
                          onClick={() => setTimeframe(tf)}
                          className={`px-4 py-1.5 rounded text-[10px] font-black transition-all ${timeframe === tf ? 'bg-blue-600 text-white' : 'text-slate-600 hover:text-slate-400'}`}
                        >
                          {tf.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {reportView === 'daily' ? (
                <div className="space-y-6">
                  {/* Top Movers Summary */}
                  <TopMovers
                    stocks={getFilteredData}
                    onSelectStock={(t) => handleStockSelect(t, 'daily')}
                  />

                  {/* Technical Signals Scanner */}
                  <TechnicalSignals
                    stocks={getFilteredData}
                    onSelectStock={(t) => handleStockSelect(t, 'daily')}
                  />

                  {/* Main Stock Table */}
                  <StockTable
                    stocks={getFilteredData}
                    visibleColumns={visibleColumns}
                    onSelectStock={(t) => handleStockSelect(t, 'daily')}
                    timeframe={timeframe}
                  />
                </div>
              ) : reportView === 'weekly' ? (
                <WeeklyReportTableV2
                  data={getFilteredData}
                  onSelectStock={(t) => handleStockSelect(t, 'weekly')}
                />
              ) : reportView === 'monthly' ? (
                <MonthlyReportTableV2
                  data={getFilteredData}
                  onSelectStock={(t) => handleStockSelect(t, 'monthly')}
                />
              ) : (
                <SeasonalityHeatmapV2
                  data={getFilteredData}
                  onSelectStock={(t) => handleStockSelect(t, 'seasonality')}
                />
              )}
            </div>
          ) : (
            /* Detail View */
            <div className="space-y-8 animate-in fade-in slide-in-from-right-2 duration-500">
              {/* Back button */}
              <button
                onClick={() => setView('table')}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
              >
                <ChevronLeft className="w-4 h-4" />
                Back to {reportView.charAt(0).toUpperCase() + reportView.slice(1)}
              </button>

              {detailSource === 'weekly' && selectedWeeklyStockData ? (
                /* Weekly Detail View */
                <>
                  <div className="flex items-end justify-between border-b border-white/5 pb-6">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-5xl font-black text-white italic">{selectedWeeklyStockData.ticker}</h2>
                        <span className={`px-4 py-1 rounded-full text-xs font-black uppercase ${
                          selectedWeeklyStockData.weekly_trend === 'UP' 
                            ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' 
                            : selectedWeeklyStockData.weekly_trend === 'DOWN'
                            ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                        }`}>
                          {selectedWeeklyStockData.weekly_trend || 'N/A'}
                        </span>
                      </div>
                      <p className="text-slate-400 text-lg uppercase font-light tracking-widest">
                        {selectedWeeklyStockData.company_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-mono text-white mb-1">₹{selectedWeeklyStockData.weekly_close?.toLocaleString()}</div>
                      <div className={`flex items-center justify-end gap-2 font-mono ${(selectedWeeklyStockData.weekly_return_pct || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        <Calendar className="h-4 w-4" />
                        <span className="text-lg">
                          {(selectedWeeklyStockData.weekly_return_pct || 0) >= 0 ? '+' : ''}
                          {selectedWeeklyStockData.weekly_return_pct?.toFixed(2)}% this week
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Weekly Stats */}
                  <WeeklyStats data={weeklyHistoricalData} ticker={selectedWeeklyStockData.ticker} />

                  {/* Weekly Charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="relative">
                      {chartsLoading && (
                        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-lg">
                          <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
                        </div>
                      )}
                      <WeeklyPriceChart data={weeklyHistoricalData} ticker={selectedWeeklyStockData.ticker} />
                    </div>
                    <div className="space-y-6">
                      <WeeklyRSIChart data={weeklyHistoricalData} ticker={selectedWeeklyStockData.ticker} />
                      <WeeklyReturnsChart data={weeklyHistoricalData} ticker={selectedWeeklyStockData.ticker} />
                    </div>
                  </div>

                  <WeeklyVolumeChart data={weeklyHistoricalData} ticker={selectedWeeklyStockData.ticker} />

                  {/* Weekly Data Table */}
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-slate-300 mb-4">Weekly Data Fields</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { label: 'Open', value: selectedWeeklyStockData.weekly_open },
                        { label: 'High', value: selectedWeeklyStockData.weekly_high },
                        { label: 'Low', value: selectedWeeklyStockData.weekly_low },
                        { label: 'Close', value: selectedWeeklyStockData.weekly_close },
                        { label: 'Volume', value: selectedWeeklyStockData.weekly_volume?.toLocaleString() },
                        { label: 'Vol Ratio', value: selectedWeeklyStockData.weekly_volume_ratio?.toFixed(2) + 'x' },
                        { label: 'RSI(14)', value: selectedWeeklyStockData.weekly_rsi14?.toFixed(1) },
                        { label: 'SMA 10', value: selectedWeeklyStockData.weekly_sma10?.toFixed(2) },
                        { label: 'SMA 20', value: selectedWeeklyStockData.weekly_sma20?.toFixed(2) },
                        { label: '4W Return', value: `${selectedWeeklyStockData.return_4w?.toFixed(2)}%` },
                        { label: '13W Return', value: `${selectedWeeklyStockData.return_13w?.toFixed(2)}%` },
                        { label: 'Week Ending', value: selectedWeeklyStockData.week_ending },
                      ].map(item => (
                        <div key={item.label} className="flex justify-between">
                          <span className="text-xs text-slate-500">{item.label}</span>
                          <span className="text-xs font-mono text-slate-300">{item.value || '-'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : detailSource === 'monthly' && selectedMonthlyStockData ? (
                /* Monthly Detail View */
                <>
                  <div className="flex items-end justify-between border-b border-white/5 pb-6">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-5xl font-black text-white italic">{selectedMonthlyStockData.ticker}</h2>
                        <span className={`px-4 py-1 rounded-full text-xs font-black uppercase ${
                          selectedMonthlyStockData.monthly_trend === 'UP' 
                            ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' 
                            : selectedMonthlyStockData.monthly_trend === 'DOWN'
                            ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20'
                            : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                        }`}>
                          {selectedMonthlyStockData.monthly_trend || 'N/A'}
                        </span>
                      </div>
                      <p className="text-slate-400 text-lg uppercase font-light tracking-widest">
                        {selectedMonthlyStockData.company_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-mono text-white mb-1">₹{selectedMonthlyStockData.monthly_close?.toLocaleString()}</div>
                      <div className={`flex items-center justify-end gap-2 font-mono ${(selectedMonthlyStockData.monthly_return_pct || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        <Calendar className="h-4 w-4" />
                        <span className="text-lg">
                          {(selectedMonthlyStockData.monthly_return_pct || 0) >= 0 ? '+' : ''}
                          {selectedMonthlyStockData.monthly_return_pct?.toFixed(2)}% this month
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Monthly Stats */}
                  <MonthlyStats data={monthlyHistoricalData} ticker={selectedMonthlyStockData.ticker} />

                  {/* Monthly Charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="relative">
                      {chartsLoading && (
                        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-lg">
                          <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
                        </div>
                      )}
                      <MonthlyPriceChart data={monthlyHistoricalData} ticker={selectedMonthlyStockData.ticker} />
                    </div>
                    <div className="space-y-6">
                      <MonthlyReturnsChart data={monthlyHistoricalData} ticker={selectedMonthlyStockData.ticker} />
                      <RollingReturnsChart data={monthlyHistoricalData} ticker={selectedMonthlyStockData.ticker} />
                    </div>
                  </div>

                  <MonthlyVolumeChart data={monthlyHistoricalData} ticker={selectedMonthlyStockData.ticker} />

                  {/* Monthly Data Table */}
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-slate-300 mb-4">Monthly Data Fields</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { label: 'Open', value: selectedMonthlyStockData.monthly_open },
                        { label: 'High', value: selectedMonthlyStockData.monthly_high },
                        { label: 'Low', value: selectedMonthlyStockData.monthly_low },
                        { label: 'Close', value: selectedMonthlyStockData.monthly_close },
                        { label: 'Volume', value: selectedMonthlyStockData.monthly_volume?.toLocaleString() },
                        { label: 'Monthly Return', value: `${selectedMonthlyStockData.monthly_return_pct?.toFixed(2)}%` },
                        { label: '3M Return', value: `${selectedMonthlyStockData.return_3m?.toFixed(2)}%` },
                        { label: '6M Return', value: `${selectedMonthlyStockData.return_6m?.toFixed(2)}%` },
                        { label: '12M Return', value: `${selectedMonthlyStockData.return_12m?.toFixed(2)}%` },
                        { label: 'YTD Return', value: `${selectedMonthlyStockData.ytd_return_pct?.toFixed(2)}%` },
                        { label: 'SMA 3', value: selectedMonthlyStockData.monthly_sma3?.toFixed(2) },
                        { label: 'SMA 6', value: selectedMonthlyStockData.monthly_sma6?.toFixed(2) },
                        { label: 'SMA 12', value: selectedMonthlyStockData.monthly_sma12?.toFixed(2) },
                        { label: 'Month', value: selectedMonthlyStockData.month },
                      ].map(item => (
                        <div key={item.label} className="flex justify-between">
                          <span className="text-xs text-slate-500">{item.label}</span>
                          <span className="text-xs font-mono text-slate-300">{item.value || '-'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : detailSource === 'seasonality' && selectedSeasonalityStockData ? (
                /* Seasonality Detail View */
                <>
                  <div className="flex items-end justify-between border-b border-white/5 pb-6">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-5xl font-black text-white italic">{selectedSeasonalityStockData.ticker}</h2>
                        <span className="px-4 py-1 rounded-full text-xs font-black uppercase bg-purple-500/10 text-purple-500 border border-purple-500/20">
                          SEASONALITY
                        </span>
                      </div>
                      <p className="text-slate-400 text-lg uppercase font-light tracking-widest">
                        {selectedSeasonalityStockData.company_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-4">
                        <div>
                          <div className="text-xs text-slate-500 uppercase mb-1">Best Month</div>
                          <div className="text-xl font-mono text-emerald-500">{selectedSeasonalityStockData.best_month || '-'}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500 uppercase mb-1">Worst Month</div>
                          <div className="text-xl font-mono text-rose-500">{selectedSeasonalityStockData.worst_month || '-'}</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Seasonality Stats */}
                  <SeasonalityStats data={seasonalityDetailData} ticker={selectedSeasonalityStockData.ticker} />

                  {/* Seasonality Charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="relative">
                      {chartsLoading && (
                        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-lg">
                          <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
                        </div>
                      )}
                      <SeasonalityBarChart data={seasonalityDetailData} ticker={selectedSeasonalityStockData.ticker} />
                    </div>
                    <SeasonalityRadarChart data={seasonalityDetailData} ticker={selectedSeasonalityStockData.ticker} />
                  </div>

                  <QuarterlyBreakdown data={seasonalityDetailData} ticker={selectedSeasonalityStockData.ticker} />

                  {/* Seasonality Data Table */}
                  <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-slate-300 mb-4">Monthly Average Returns</h3>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                      {[
                        { label: 'January', value: selectedSeasonalityStockData.jan_avg },
                        { label: 'February', value: selectedSeasonalityStockData.feb_avg },
                        { label: 'March', value: selectedSeasonalityStockData.mar_avg },
                        { label: 'April', value: selectedSeasonalityStockData.apr_avg },
                        { label: 'May', value: selectedSeasonalityStockData.may_avg },
                        { label: 'June', value: selectedSeasonalityStockData.jun_avg },
                        { label: 'July', value: selectedSeasonalityStockData.jul_avg },
                        { label: 'August', value: selectedSeasonalityStockData.aug_avg },
                        { label: 'September', value: selectedSeasonalityStockData.sep_avg },
                        { label: 'October', value: selectedSeasonalityStockData.oct_avg },
                        { label: 'November', value: selectedSeasonalityStockData.nov_avg },
                        { label: 'December', value: selectedSeasonalityStockData.dec_avg },
                      ].map(item => (
                        <div key={item.label} className="flex flex-col items-center p-2 rounded-lg bg-slate-800/50">
                          <span className="text-[10px] text-slate-500 uppercase mb-1">{item.label.slice(0, 3)}</span>
                          <span className={`text-sm font-mono ${(item.value || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {item.value != null ? `${item.value >= 0 ? '+' : ''}${item.value.toFixed(2)}%` : '-'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : selectedStockData ? (
                /* Daily Detail View */
                <>
                  {/* Detail Hero */}
                  <div className="flex items-end justify-between border-b border-white/5 pb-6">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-5xl font-black text-white italic">{selectedStockData.ticker}</h2>
                        <span className={`px-4 py-1 rounded-full text-xs font-black uppercase ${selectedStockData.overall_score > 70 ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'}`}>
                          SCORE: {selectedStockData.overall_score?.toFixed(1)}
                        </span>
                      </div>
                      <p className="text-slate-400 text-lg uppercase font-light tracking-widest">{selectedStockData.company_name}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-mono text-white mb-1">₹{selectedStockData.price_last?.toLocaleString()}</div>
                      <div className={`flex items-center justify-end gap-2 font-mono ${(selectedStockData.return_1d || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        <Calendar className="h-4 w-4" />
                        <span className="text-lg">{(selectedStockData.return_1d || 0) >= 0 ? '+' : ''}{selectedStockData.return_1d?.toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Charts Section */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="relative">
                      {chartsLoading && (
                        <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-[2px] z-10 flex items-center justify-center rounded-lg">
                          <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
                        </div>
                      )}
                      <PriceChart ticker={selectedStockData.ticker} data={historicalData} />
                    </div>
                    <div className="space-y-6">
                      <RSIChart ticker={selectedStockData.ticker} data={historicalData} />
                      <MACDChart ticker={selectedStockData.ticker} data={historicalData} />
                    </div>
                  </div>

                  {/* Analysis Matrix - THE 110 FIELDS */}
                  <div className="space-y-6">
                    <h3 className="text-xs font-black text-slate-500 tracking-[0.2em] uppercase flex items-center gap-4">
                      <div className="h-px flex-1 bg-white/5"></div>
                      DEEP DIVE ANALYSIS MATRIX
                      <div className="h-px flex-1 bg-white/5"></div>
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                      {['Fundamental', 'Technical', 'Scores', 'Analysis'].map(group => (
                        <div key={group} className="bg-[#0a101f] border border-white/5 rounded-xl p-5 shadow-inner">
                          <h4 className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            {group === 'Fundamental' && <ShieldCheck className="h-3 w-3" />}
                            {group === 'Technical' && <TrendingUp className="h-3 w-3" />}
                            {group === 'Analysis' && <Info className="h-3 w-3" />}
                            {group}
                          </h4>
                          <div className="space-y-3">
                            {ALL_FIELDS.filter(f => f.group === group).map(field => {
                              const value = selectedStockData[field.id];
                              return (
                                <div key={field.id} className="flex justify-between items-center group">
                                  <span className="text-[10px] text-slate-500 uppercase group-hover:text-slate-300 transition-colors">{field.label}</span>
                                  <span className="text-[10px] font-mono text-slate-300">
                                    {typeof value === 'number'
                                      ? (field.id.includes('pct') || field.id.includes('return') ? `${value.toFixed(2)}%` : value.toLocaleString(undefined, { maximumFractionDigits: 2 }))
                                      : (value || '-')}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Qualitative Notes Card */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                      {['Moat Notes', 'Risk Notes', 'Catalysts'].map(note => (
                        <div key={note} className="bg-[#0a101f] border border-white/5 rounded-xl p-5">
                          <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest mb-3">{note}</h4>
                          <div className="text-xs text-slate-400 leading-relaxed italic">
                            {selectedStockData[note.toLowerCase().replace(' ', '_')] || `No qualitative ${note.toLowerCase()} recorded for this session.`}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-40 grayscale">
                  <TrendingUp className="h-24 w-24 text-slate-800 mb-6" />
                  <h3 className="text-2xl font-black tracking-tighter uppercase italic">Select Assets For Detailed Telemetry</h3>
                  <p className="text-slate-600 max-w-sm mt-2 text-sm">Select a security to view detailed analysis.</p>
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {showColumnPicker && (
        <div className="fixed right-20 top-20 z-[100] w-80 bg-[#0f172a] border border-white/10 rounded-lg shadow-2xl p-4 ring-1 ring-white/10 animate-in zoom-in-95 duration-200">
          <h3 className="text-xs font-black uppercase tracking-widest mb-3 border-b border-white/5 pb-2 flex justify-between items-center text-slate-400">
            {reportView.charAt(0).toUpperCase() + reportView.slice(1)} Columns
            <button onClick={() => setShowColumnPicker(false)} className="text-rose-500 hover:text-white transition-colors">CLOSE</button>
          </h3>
          <div className="max-h-96 overflow-y-auto space-y-4 pr-1 scrollbar-thin scrollbar-thumb-slate-800">
            {Array.from(new Set(currentFields.map(f => f.group))).map(group => (
              <div key={group}>
                <h4 className="text-[9px] font-black text-slate-600 uppercase tracking-[0.2em] mb-2">{group}</h4>
                <div className="grid grid-cols-1 gap-1">
                  {currentFields.filter(f => f.group === group).map(field => (
                    <label key={field.id} className="flex items-center gap-3 hover:bg-white/5 p-1.5 rounded cursor-pointer transition-colors group">
                      <input
                        type="checkbox"
                        checked={currentVisibleColumns.includes(field.id)}
                        onChange={() => toggleCurrentColumn(field.id)}
                        className="rounded border-white/10 bg-slate-800 text-blue-600 focus:ring-0"
                      />
                      <span className="text-[10px] uppercase font-bold text-slate-400 group-hover:text-blue-400 transition-colors">{field.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
