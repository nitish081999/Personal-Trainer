"use client";

import { useState } from "react";
import Head from "next/head";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const startMining = async () => {
    setLoading(true);
    setLogs(prev => [...prev, "🚀 Initializing AI Orchestrator..."]);

    setTimeout(() => setLogs(prev => [...prev, "🤖 Routing to Groq for MCQ Generation (Fallback: Mistral)..."]), 1000);
    setTimeout(() => setLogs(prev => [...prev, "🔍 Querying Tavily & Serper for Political Science topics..."]), 2500);
    setTimeout(() => setLogs(prev => [...prev, "🧠 Structuring raw content strictly with Gemini JSON mode..."]), 4500);
    setTimeout(() => setLogs(prev => [...prev, "🧬 Deduplication Engine hash check complete (0 duplicates)..."]), 6000);
    setTimeout(() => {
      setLogs(prev => [...prev, "✅ Inserted 10 high-quality MCQs to Postgres Database."]);
      setLoading(false);
    }, 7500);
  };

  return (
    <div className="min-h-screen font-[var(--font-sans)] flex flex-col items-center py-16 px-4 sm:px-8">
      <Head>
        <title>Personal Trainer AI</title>
        <meta name="description" content="AI-Powered SSC & Competitive Exam Prep Orchestrator" />
      </Head>

      {/* Hero Section */}
      <header className="text-center space-y-6 max-w-4xl w-full slide-down blur-in animate-pulse-slow">
        <div className="inline-block glass-panel px-6 py-2 rounded-full mb-4 text-cyan-400 font-semibold uppercase tracking-widest text-sm">
          A Deepmind Agent Project
        </div>
        <h1 className="text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-tight">
          Supercharge Your Prep with <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 text-glow">Multi-Model AI</span>
        </h1>
        <p className="text-xl md:text-2xl text-slate-300 font-light max-w-2xl mx-auto">
          An intelligent orchestration layer routing between Groq, Gemini & Mistral to dynamically mine, deduplicate, and generate adaptive tests every single day.
        </p>
      </header>

      {/* Interactive Mining Demo */}
      <section className="mt-20 w-full max-w-3xl glass-card p-10 flex flex-col items-center">
        <h2 className="text-3xl font-bold mb-6 text-white text-center">Trigger Mining Engine</h2>
        <p className="mb-8 text-slate-400 text-center">Simulate the daily background job orchestrating LLMs to generate 100 new questions across 6 subjects.</p>

        <button
          onClick={startMining}
          disabled={loading}
          className="relative inline-flex items-center justify-center px-10 py-4 font-bold text-white transition-all duration-300 rounded-xl bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_30px_rgba(168,85,247,0.5)] transform hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Orchestrating...
            </span>
          ) : (
            "▶ Mine 'Indian Polity' Questions"
          )}
        </button>

        {/* Real-time Logs Output */}
        {logs.length > 0 && (
          <div className="w-full mt-10 p-6 bg-slate-900/80 rounded-xl border border-slate-700/60 font-mono text-sm shadow-inner transition-all duration-500">
            <div className="flex items-center gap-3 mb-4 pb-2 border-b border-slate-700/50">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="text-slate-400">orchestrator.log</span>
            </div>
            <div className="space-y-3 h-48 overflow-y-auto pr-2 custom-scrollbar">
              {logs.map((log, idx) => (
                <div key={idx} className="flex gap-3 text-slate-300 animate-fade-in">
                  <span className="text-cyan-500">[{new Date().toISOString().split("T")[1].substring(0, 8)}]</span>
                  <p>{log}</p>
                </div>
              ))}
              {loading && <div className="text-slate-500 animate-pulse">_</div>}
            </div>
          </div>
        )}
      </section>

      {/* Architecture Cards */}
      <section className="mt-24 w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {[
          { icon: "🧠", title: "LLM Router", desc: "Dynamic fallback between Groq, Gemini & Mistral respecting rate limits." },
          { icon: "🌐", title: "Search APIs", desc: "Rotates over Tavily, Serper, and DuckDuckGo to mine raw subject matter." },
          { icon: "⛓️", title: "JSON Structuring", desc: "Extracts strictly typed MCQs from raw webpages using structured LLM calls." },
          { icon: "🛡️", title: "Deduplication", desc: "Hashes incoming queries against PostgreSQL to maintain a premium Q-bank." },
          { icon: "📊", title: "Adaptive Engine", desc: "Calculates recent-weighted weakness per topic to dynamically generate revision tests." },
          { icon: "⏱️", title: "Daily Cron Job", desc: "Fully automated, mining 100 topic-rotated questions for 6 subjects across the night." }
        ].map((feat, i) => (
          <div key={i} className="glass-card p-8 flex flex-col gap-4 text-left transition-transform duration-300 hover:-translate-y-2">
            <div className="text-4xl bg-slate-800/80 w-16 h-16 rounded-xl flex items-center justify-center shadow-[inset_0_2px_4px_rgba(255,255,255,0.1)] border border-slate-700">
              {feat.icon}
            </div>
            <h3 className="text-xl font-bold text-white tracking-wide">{feat.title}</h3>
            <p className="text-slate-400 font-light leading-relaxed">{feat.desc}</p>
          </div>
        ))}
      </section>

    </div>
  );
}
