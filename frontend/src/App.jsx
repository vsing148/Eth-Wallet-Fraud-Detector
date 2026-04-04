import React, { useState, useEffect } from 'react';

export default function App() {
  const [address, setAddress] = useState('');
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [maxRecords, setMaxRecords] = useState('200');

  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Fetching on-chain data...');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [riskWidth, setRiskWidth] = useState(0);

  const loadingMessages = [
    'Fetching on-chain data...',
    'Extracting 45 Kaggle features...',
    'Scaling features via StandardScaler...',
    'Running GCN inference...',
    'Computing fraud probability...'
  ];

  // Handle the rotating loading text
  useEffect(() => {
    let interval;
    if (loading) {
      let i = 0;
      setLoadingText(loadingMessages[0]);
      interval = setInterval(() => {
        i = (i + 1) % loadingMessages.length;
        setLoadingText(loadingMessages[i]);
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Handle the progress bar animation when data loads
  useEffect(() => {
    if (data) {
      setTimeout(() => setRiskWidth(data.fraud_probability_percent), 80);
    } else {
      setRiskWidth(0);
    }
  }, [data]);

  const runScan = async (e) => {
    if (e) e.preventDefault();

    const trimmedAddr = address.trim();
    if (!/^0x[a-fA-F0-9]{40}$/.test(trimmedAddr)) {
      setError("Invalid Ethereum address format.");
      setData(null);
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    const baseUrl = apiUrl.trim().replace(/\/$/, '');

    try {
      const res = await fetch(`${baseUrl}/analyze/${trimmedAddr}?max_records=${maxRecords}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        throw new Error(err.detail || `Server returned ${res.status}`);
      }
      const result = await res.json();
      setData(result);
    } catch (err) {
      setError(`Could not reach API at ${baseUrl}. Is your FastAPI server running?\n\n${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const isFraud = data?.prediction === "Fraudulent/Suspicious";
  const riskLevel = data ? (data.fraud_probability_percent < 30 ? 'low' : data.fraud_probability_percent < 65 ? 'mid' : 'high') : 'low';

  const riskColors = {
    low: '#00e676',
    mid: '#ffd740',
    high: '#ff5252'
  };

  const getRiskColor = () => riskColors[riskLevel];

  return (
    <div className="min-h-screen bg-[#090c0b] text-[#e8f0ea] font-sans flex flex-col items-center pt-[60px] pb-[80px] px-5 selection:bg-[#00e676]/30">

      {/* Injecting custom keyframes for the scan animation */}
      <style>{`
        
        .font-mono-custom { font-family: 'JetBrains Mono', monospace; }
        .font-sans-custom { font-family: 'DM Sans', sans-serif; }
        
        @keyframes scan {
          0% { width: 0%; margin-left: 0%; }
          50% { width: 60%; margin-left: 20%; }
          100% { width: 0%; margin-left: 100%; }
        }
        .animate-scan { animation: scan 2.4s ease-in-out infinite; }
      `}</style>

      {/* ── HEADER ── */}
      <header className="text-center mb-14">
        <div className="inline-flex items-center gap-1.5 font-mono-custom text-[10px] font-medium tracking-[0.12em] uppercase text-[#00e676] border border-[#243029] py-[5px] px-3 rounded-[3px] mb-6">
          <span className="w-[5px] h-[5px] rounded-full bg-[#00e676] animate-pulse"></span>
          GNN Inference Live
        </div>
        <h1 className="font-mono-custom text-3xl md:text-[38px] font-light tracking-[-0.02em] leading-tight mb-3">
          Ethereum <span className="text-[#00e676] font-semibold">Fraud</span> Scanner
        </h1>
        <p className="text-[14px] text-[#7a9882] font-light tracking-[0.01em]">
          Graph Neural Network · 45 on-chain features · 3-layer GCN · Etherscan live data
        </p>
      </header>

      {/* ── INPUT CARD ── */}
      <div className="w-full max-w-[760px] bg-[#111714] border border-[#1e2b22] rounded-md p-6 md:p-8 mb-8">
        <label className="font-mono-custom text-[10px] font-medium tracking-[0.1em] uppercase text-[#3e5445] mb-2.5 block">
          Wallet Address
        </label>
        <form onSubmit={runScan} className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="0x742d35Cc6634C0532925a3b8D4f9c8F..."
            className={`flex-1 bg-[#090c0b] border ${error && !data ? 'border-[#ff5252]' : 'border-[#243029]'} rounded focus:border-[#00e676] py-3.5 px-4 font-mono-custom text-[13px] text-[#e8f0ea] tracking-[0.04em] outline-none transition-colors min-w-0`}
            spellCheck="false"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-[#00e676] text-[#001a0a] border-none rounded py-3.5 px-7 font-mono-custom text-[12px] font-semibold tracking-[0.08em] uppercase cursor-pointer whitespace-nowrap transition-all hover:opacity-85 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            Scan
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-5 mt-4">
          <div className="flex items-center gap-2 text-[12px] text-[#7a9882]">
            <span className="font-mono-custom text-[11px] text-[#3e5445]">API endpoint</span>
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              className="bg-transparent border-b border-[#243029] focus:border-[#00e676] pb-0.5 font-mono-custom text-[11px] text-[#00e676] outline-none w-[200px]"
            />
          </div>
          <div className="flex items-center gap-2 text-[12px] text-[#7a9882]">
            <span className="font-mono-custom text-[11px] text-[#3e5445]">max records</span>
            <select
              value={maxRecords}
              onChange={(e) => setMaxRecords(e.target.value)}
              className="bg-transparent border-b border-[#243029] text-[#00e676] font-mono-custom text-[11px] outline-none pb-0.5 cursor-pointer"
            >
              <option value="100" className="bg-[#111714]">100</option>
              <option value="200" className="bg-[#111714]">200</option>
              <option value="500" className="bg-[#111714]">500</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── LOADING ── */}
      {loading && (
        <div className="w-full max-w-[760px] bg-[#111714] border border-[#1e2b22] rounded-md py-12 px-9 text-center mb-8 animate-pulse">
          <div className="w-full h-[2px] bg-[#1e2b22] rounded-sm overflow-hidden mb-6">
            <div className="h-full bg-[#00e676] animate-scan"></div>
          </div>
          <div className="font-mono-custom text-[12px] text-[#7a9882] tracking-[0.06em]">
            {loadingText}
          </div>
          <div className="font-mono-custom text-[11px] text-[#3e5445] mt-1.5 break-all">
            {address}
          </div>
        </div>
      )}

      {/* ── ERROR ── */}
      {error && !loading && !data && (
        <div className="w-full max-w-[760px] bg-[#111714] border border-[#ff5252]/30 rounded-md py-6 px-8 mb-8">
          <div className="font-mono-custom text-[11px] tracking-[0.08em] uppercase text-[#ff5252] mb-1.5">
            Scan failed
          </div>
          <div className="text-[13px] text-[#7a9882] whitespace-pre-wrap">
            {error}
          </div>
        </div>
      )}

      {/* ── RESULTS ── */}
      {data && !loading && (
        <div className="w-full max-w-[760px] flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">

          {/* Verdict Card */}
          <div className="bg-[#111714] border border-[#1e2b22] rounded-md py-8 px-6 md:px-9">
            <div className="flex flex-col md:flex-row justify-between items-start gap-5 mb-7">
              <div>
                <div className="font-mono-custom text-[10px] tracking-[0.12em] uppercase text-[#3e5445] mb-2">
                  Analyzed address
                </div>
                <div className="font-mono-custom text-[13px] text-[#7a9882] break-all max-w-[420px]">
                  {data.wallet_address.slice(0, -6)}
                  <em className="not-italic text-[#e8f0ea] font-medium">{data.wallet_address.slice(-6)}</em>
                </div>
              </div>
              <div className={`inline-block font-mono-custom text-[11px] font-semibold tracking-[0.08em] uppercase py-2 px-4 rounded-[3px] shrink-0 border ${isFraud ? 'bg-[#ff5252]/10 text-[#ff5252] border-[#ff5252]/30' : 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30'
                }`}>
                {data.prediction}
              </div>
            </div>

            <div className="mb-1">
              <div className="flex justify-between items-baseline mb-2.5">
                <div className="font-mono-custom text-[10px] tracking-[0.1em] uppercase text-[#3e5445]">
                  Fraud probability
                </div>
                <div className="font-mono-custom text-[28px] font-light leading-none" style={{ color: getRiskColor() }}>
                  {data.fraud_probability_percent.toFixed(1)}%
                </div>
              </div>
              <div className="w-full h-[6px] bg-[#1e2b22] rounded-[3px] overflow-hidden mb-2">
                <div
                  className="h-full rounded-[3px] transition-all duration-1000 ease-[cubic-bezier(0.16,1,0.3,1)]"
                  style={{ width: `${riskWidth}%`, backgroundColor: getRiskColor() }}
                ></div>
              </div>
              <div className="flex justify-between font-mono-custom text-[9px] text-[#3e5445] tracking-[0.06em]">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div className="bg-[#182019] border border-[#1e2b22] rounded-[5px] py-4 px-5">
              <div className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445] mb-2">Total transactions</div>
              <div className="font-mono-custom text-[22px] font-light text-[#e8f0ea] leading-none">
                {data.top_features['Total Txs'].toLocaleString()}
              </div>
            </div>
            <div className="bg-[#182019] border border-[#1e2b22] rounded-[5px] py-4 px-5">
              <div className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445] mb-2">ETH Balance</div>
              <div className="font-mono-custom text-[22px] font-light text-[#e8f0ea] leading-none">
                <span className="text-[11px] text-[#7a9882] ml-0.5 mr-1">Ξ</span>
                {data.top_features['ETH Balance'].toFixed(4)}
              </div>
            </div>
            <div className="bg-[#182019] border border-[#1e2b22] rounded-[5px] py-4 px-5 col-span-2 md:col-span-1">
              <div className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445] mb-2">ERC-20 transfers</div>
              <div className="font-mono-custom text-[22px] font-light text-[#e8f0ea] leading-none">
                {data.top_features['ERC20 Txs'].toLocaleString()}
              </div>
            </div>
          </div>

          {/* Features Card */}
          <div className="bg-[#111714] border border-[#1e2b22] rounded-md py-6 px-6 md:px-9">
            <div className="font-mono-custom text-[10px] tracking-[0.1em] uppercase text-[#3e5445] mb-4">
              Feature Snapshot — Live on-chain signals
            </div>

            <div className="flex justify-between items-center py-2.5 border-b border-[#1e2b22]">
              <span className="font-mono-custom text-[11px] text-[#7a9882]">normal_txs_analyzed</span>
              <span className="font-mono-custom text-[12px] font-medium text-[#e8f0ea]">{data.normal_txs_analyzed}</span>
            </div>
            <div className="flex justify-between items-center py-2.5 border-b border-[#1e2b22]">
              <span className="font-mono-custom text-[11px] text-[#7a9882]">erc20_txs_analyzed</span>
              <span className="font-mono-custom text-[12px] font-medium text-[#e8f0ea]">{data.erc20_txs_analyzed}</span>
            </div>
            <div className="flex justify-between items-center py-2.5 border-b border-[#1e2b22]">
              <span className="font-mono-custom text-[11px] text-[#7a9882]">total_ether_balance</span>
              <span className="font-mono-custom text-[12px] font-medium text-[#e8f0ea]">Ξ {data.top_features['ETH Balance'].toFixed(6)}</span>
            </div>
            <div className="flex justify-between items-center py-2.5 border-b border-[#1e2b22]">
              <span className="font-mono-custom text-[11px] text-[#7a9882]">total_ether_transactions</span>
              <span className="font-mono-custom text-[12px] font-medium text-[#e8f0ea]">{data.top_features['Total Txs']}</span>
            </div>
            <div className="flex justify-between items-center py-2.5">
              <span className="font-mono-custom text-[11px] text-[#7a9882]">raw_prediction_class</span>
              <span className="font-mono-custom text-[12px] font-medium text-[#e8f0ea]">{isFraud ? '1 (fraud)' : '0 (normal)'}</span>
            </div>
          </div>

          {/* Model Tag */}
          <div className="flex flex-wrap items-center gap-6 py-4 px-6 bg-[#182019] border border-[#1e2b22] rounded-[5px]">
            <div className="flex flex-col gap-1">
              <span className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445]">Architecture</span>
              <span className="font-mono-custom text-[11px] text-[#7a9882]">FraudGNN — 3-layer GCN</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445]">Features</span>
              <span className="font-mono-custom text-[11px] text-[#7a9882]">45 Kaggle-mapped</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="font-mono-custom text-[9px] tracking-[0.1em] uppercase text-[#3e5445]">Graph edges</span>
              <span className="font-mono-custom text-[11px] text-[#7a9882]">k-NN (k=5) + self-loop</span>
            </div>
          </div>

        </div>
      )}

      {/* ── FOOTER ── */}
      <footer className="mt-16 font-mono-custom text-[10px] tracking-[0.08em] text-[#3e5445] text-center">
        eth-fraud-detector · gnn inference client · v1.0
      </footer>

    </div>
  );
}