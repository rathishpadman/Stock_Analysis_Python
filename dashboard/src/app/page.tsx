'use client';

import React, { useState, useEffect } from 'react';
import StockTable from '@/components/StockTable';
import { ScoreBarChart, PriceChart, RSIChart } from '@/components/Charts';
import { ALL_FIELDS, DEFAULT_COLUMNS } from '@/lib/constants';
import { Settings2, Search, Filter, LogOut, Loader2, BarChart3 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function DashboardPage() {
  const { user, loading: authLoading, signInWithGoogle, signOut } = useAuth();
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLocalTest, setIsLocalTest] = useState(false);
  const [visibleColumns, setVisibleColumns] = useState(DEFAULT_COLUMNS);
  const [searchQuery, setSearchQuery] = useState('');
  const [showColumnPicker, setShowColumnPicker] = useState(false);
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [showCharts, setShowCharts] = useState(true);

  useEffect(() => {
    if (!authLoading && user) {
      fetchStocks();
    }
  }, [user, authLoading]);

  const fetchStocks = async () => {
    setLoading(true);
    if (isLocalTest) {
      // Use mock data for testing
      setStocks([
        { ticker: 'RELIANCE', company_name: 'Reliance Industries', price_last: 1565.10, return_1d: 0.55, overall_score: 82.5, rsi14: 65.2, sector: 'Energy', pe_ttm: 25.4 },
        { ticker: 'TCS', company_name: 'Tata Consultancy Services', price_last: 3850.40, return_1d: -1.2, overall_score: 78.1, rsi14: 45.8, sector: 'IT', pe_ttm: 30.1 },
        { ticker: 'HDFCBANK', company_name: 'HDFC Bank', price_last: 1620.00, return_1d: 0.1, overall_score: 85.4, rsi14: 58.9, sector: 'Finance', pe_ttm: 18.2 },
        { ticker: 'INFY', company_name: 'Infosys', price_last: 1450.75, return_1d: 0.8, overall_score: 75.2, rsi14: 52.1, sector: 'IT', pe_ttm: 22.5 },
        { ticker: 'ICICIBANK', company_name: 'ICICI Bank', price_last: 980.50, return_1d: -0.3, overall_score: 72.8, rsi14: 48.3, sector: 'Finance', pe_ttm: 16.8 },
        { ticker: 'HINDUNILVR', company_name: 'Hindustan Unilever', price_last: 2520.00, return_1d: 0.2, overall_score: 68.5, rsi14: 55.7, sector: 'FMCG', pe_ttm: 58.2 },
        { ticker: 'BAJFINANCE', company_name: 'Bajaj Finance', price_last: 7250.00, return_1d: 1.5, overall_score: 79.3, rsi14: 62.4, sector: 'Finance', pe_ttm: 35.1 },
        { ticker: 'BHARTIARTL', company_name: 'Bharti Airtel', price_last: 1125.30, return_1d: 0.9, overall_score: 81.2, rsi14: 68.9, sector: 'Telecom', pe_ttm: 45.3 },
        { ticker: 'SBIN', company_name: 'State Bank of India', price_last: 625.40, return_1d: -0.5, overall_score: 55.1, rsi14: 38.2, sector: 'Finance', pe_ttm: 9.8 },
        { ticker: 'MARUTI', company_name: 'Maruti Suzuki', price_last: 10850.00, return_1d: 0.7, overall_score: 71.6, rsi14: 54.8, sector: 'Auto', pe_ttm: 28.4 },
      ]);
      setLoading(false);
      return;
    }
    try {
      const res = await fetch('/api/stocks');
      const data = await res.json();
      setStocks(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (id: string) => {
    setVisibleColumns(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    );
  };

  if (authLoading) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
    </div>
  );

  if (!user && !isLocalTest) return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full text-center space-y-8 bg-slate-900 border border-slate-800 p-12 rounded-2xl shadow-2xl">
        <h1 className="text-4xl font-extrabold text-white tracking-tight">Stock Pipeline</h1>
        <p className="text-slate-400">Sign in with Google to access your dashboard and analyzed metrics.</p>
        <div className="space-y-4">
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
            Continue with Google
          </button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-slate-800"></span></div>
            <div className="relative flex justify-center text-xs uppercase"><span className="bg-slate-900 px-2 text-slate-500 font-bold">Or</span></div>
          </div>

          <button
            onClick={() => {
              setIsLocalTest(true);
              setLoading(true);
              // Trigger reload in local mode
              setTimeout(() => {
                setStocks([
                  { ticker: 'RELIANCE', company_name: 'Reliance Industries', price_last: 1565.10, return_1d: 0.55, overall_score: 82.5, rsi14: 65.2, sector: 'Energy', pe_ttm: 25.4 },
                  { ticker: 'TCS', company_name: 'Tata Consultancy Services', price_last: 3850.40, return_1d: -1.2, overall_score: 78.1, rsi14: 45.8, sector: 'IT', pe_ttm: 30.1 },
                  { ticker: 'HDFCBANK', company_name: 'HDFC Bank', price_last: 1620.00, return_1d: 0.1, overall_score: 85.4, rsi14: 58.9, sector: 'Finance', pe_ttm: 18.2 },
                ]);
                setLoading(false);
              }, 500);
            }}
            className="w-full bg-slate-800 text-slate-300 font-medium py-2.5 px-6 rounded-lg hover:bg-slate-700 transition-all border border-slate-700"
          >
            Enter Local Test Mode (No Auth)
          </button>
        </div>
      </div>
    </div>
  );

  const filteredStocks = stocks.filter(s =>
    s.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Stock Analysis Pipeline</h1>
          <p className="text-slate-400">Real-time enrichment and multi-timeframe analysis for traders.</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search ticker or company..."
              className="bg-slate-900 border border-slate-700 rounded-md pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 transition-all w-64 text-white"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <button
            onClick={() => setShowCharts(!showCharts)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm border ${showCharts ? 'bg-blue-900/30 border-blue-800 text-blue-300' : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'}`}
          >
            <BarChart3 className="h-4 w-4" />
            {showCharts ? 'Hide Analytics' : 'Show Analytics'}
          </button>

          <button
            onClick={() => setShowColumnPicker(!showColumnPicker)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors text-sm border ${showColumnPicker ? 'bg-blue-900/30 border-blue-800 text-blue-300' : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'}`}
          >
            <Settings2 className="h-4 w-4" />
            Customize View
          </button>

          <button
            onClick={user ? signOut : () => setIsLocalTest(false)}
            className="flex items-center gap-2 bg-rose-950/30 hover:bg-rose-900/50 border border-rose-900/50 px-4 py-2 rounded-md transition-colors text-sm text-rose-300"
          >
            <LogOut className="h-4 w-4" />
            {user ? 'Sign Out' : 'Exit Test Mode'}
          </button>
        </div>
      </header>

      {/* Column Picker Modal */}
      {showColumnPicker && (
        <div className="absolute right-32 top-24 z-50 w-80 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl p-4 ring-1 ring-white/10">
          <h3 className="text-lg font-semibold mb-3 border-b border-slate-700 pb-2 flex justify-between items-center">
            Toggle Columns
            <button onClick={() => setShowColumnPicker(false)} className="text-slate-500 hover:text-white text-sm">Done</button>
          </h3>
          <div className="max-h-96 overflow-y-auto space-y-4">
            {['Basic', 'Price', 'Fundamental', 'Technical', 'Scores', 'Metadata'].map(group => (
              <div key={group}>
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">{group}</h4>
                <div className="grid grid-cols-1 gap-1">
                  {ALL_FIELDS.filter(f => f.group === group).map(field => (
                    <label key={field.id} className="flex items-center gap-3 hover:bg-slate-800 p-1.5 rounded cursor-pointer transition-colors group">
                      <input
                        type="checkbox"
                        checked={visibleColumns.includes(field.id)}
                        onChange={() => toggleColumn(field.id)}
                        className="rounded border-slate-600 bg-slate-800 text-blue-600 focus:ring-offset-slate-900"
                      />
                      <span className="text-sm group-hover:text-blue-400 transition-colors">{field.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <main className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg shadow-sm">
            <div className="text-xs font-medium text-slate-500 uppercase">Universe</div>
            <div className="text-2xl font-bold text-white">{stocks.length} Stocks</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg border-l-emerald-500 border-l-4 shadow-sm">
            <div className="text-xs font-medium text-slate-500 uppercase">Bullish Setup</div>
            <div className="text-2xl font-bold text-white">{stocks.filter(s => (s.overall_score || 0) > 70).length}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg border-l-rose-500 border-l-4 shadow-sm">
            <div className="text-xs font-medium text-slate-500 uppercase">Bearish Setup</div>
            <div className="text-2xl font-bold text-white">{stocks.filter(s => (s.overall_score || 0) < 40).length}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg border-l-amber-500 border-l-4 shadow-sm">
            <div className="text-xs font-medium text-slate-500 uppercase">Neutral/Sideways</div>
            <div className="text-2xl font-bold text-white">{stocks.filter(s => (s.overall_score || 0) >= 40 && (s.overall_score || 0) <= 70).length}</div>
          </div>
        </div>

        {showCharts && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <ScoreBarChart stocks={stocks} />
            </div>
            <div className="lg:col-span-2 space-y-6">
              {selectedStock ? (
                <div className="space-y-6">
                  <PriceChart
                    ticker={selectedStock}
                    data={[
                      { date: '2024-01-01', price: 1500, sma20: 1480, sma50: 1450, rsi: 45 },
                      { date: '2024-01-02', price: 1520, sma20: 1485, sma50: 1455, rsi: 52 },
                      { date: '2024-01-03', price: 1510, sma20: 1490, sma50: 1460, rsi: 48 },
                      { date: '2024-01-04', price: 1550, sma20: 1500, sma50: 1470, rsi: 65 },
                      { date: '2024-01-05', price: 1565, sma20: 1515, sma50: 1480, rsi: 72 },
                    ]}
                  />
                  <RSIChart
                    ticker={selectedStock}
                    data={[
                      { date: '2024-01-01', price: 1500, rsi: 45 },
                      { date: '2024-01-02', price: 1520, rsi: 52 },
                      { date: '2024-01-03', price: 1510, rsi: 48 },
                      { date: '2024-01-04', price: 1550, rsi: 65 },
                      { date: '2024-01-05', price: 1565, rsi: 72 },
                    ]}
                  />
                </div>
              ) : (
                <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-slate-900 border border-slate-800 rounded-lg p-8 text-center">
                  <BarChart3 className="h-12 w-12 text-slate-700 mb-4" />
                  <h4 className="text-xl font-bold text-slate-300">No Stock Selected</h4>
                  <p className="text-slate-500 max-w-xs mt-2">Click on a ticker in the table below to see detailed price and technical analysis.</p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-slate-400 mb-2 overflow-x-auto pb-2">
          <Filter className="h-4 w-4 flex-shrink-0" />
          <span>Active Filters:</span>
          <span className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded border border-slate-700 text-xs flex-shrink-0">ALL STOCKS</span>
          {searchQuery && (
            <span className="bg-blue-900/30 text-blue-300 px-2 py-0.5 rounded border border-blue-800/50 text-xs flex items-center gap-1 flex-shrink-0">
              Search: {searchQuery}
              <button onClick={() => setSearchQuery('')} className="hover:text-white">×</button>
            </span>
          )}
        </div>

        {loading ? (
          <div className="h-96 w-full flex flex-col items-center justify-center bg-slate-900 rounded-lg border border-slate-800 gap-3">
            <Loader2 className="h-10 w-10 text-blue-600 animate-spin" />
            <p className="text-slate-400 animate-pulse">Fetching latest snapshots from Supabase...</p>
          </div>
        ) : (
          <StockTable
            stocks={filteredStocks}
            visibleColumns={visibleColumns}
            onSelectStock={setSelectedStock}
          />
        )}
      </main>
    </div>
  );
}
