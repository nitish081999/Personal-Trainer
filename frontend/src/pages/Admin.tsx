import { useEffect, useState } from "react";
import {
  Database,
  Cpu,
  RefreshCw,
  ArrowLeft,
  Pickaxe,
} from "lucide-react";
import {
  getSubjects,
  getMiningLogs,
  getAPIUsage,
  triggerMining,
  triggerMiningAll,
} from "@/lib/api";
import type { Subject, MiningLog, APIUsage, MiningResult } from "@/types/api";

interface AdminProps {
  onNavigate: (page: string) => void;
}

export default function AdminPage({ onNavigate }: AdminProps) {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [logs, setLogs] = useState<MiningLog[]>([]);
  const [apiUsage, setApiUsage] = useState<APIUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [mining, setMining] = useState<number | null>(null);
  const [miningAll, setMiningAll] = useState(false);
  const [lastResult, setLastResult] = useState<MiningResult | null>(null);

  const loadData = async () => {
    try {
      const [subs, mLogs, usage] = await Promise.all([
        getSubjects(),
        getMiningLogs({ limit: 20 }),
        getAPIUsage(),
      ]);
      setSubjects(subs);
      setLogs(mLogs);
      setApiUsage(usage);
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleMineSubject = async (subjectId: number) => {
    setMining(subjectId);
    setLastResult(null);
    try {
      const result = await triggerMining(subjectId, 20);
      setLastResult(result);
      await loadData();
    } catch (err) {
      console.error("Mining failed:", err);
      setLastResult({ status: "failed", questions_added: 0, error: String(err) });
    } finally {
      setMining(null);
    }
  };

  const handleMineAll = async () => {
    setMiningAll(true);
    setLastResult(null);
    try {
      const result = await triggerMiningAll(20);
      const totalAdded = result.results.reduce(
        (sum, r) => sum + r.questions_added,
        0
      );
      setLastResult({
        status: "completed",
        questions_added: totalAdded,
        subject: "All Subjects",
      });
      await loadData();
    } catch (err) {
      console.error("Mining all failed:", err);
      setLastResult({ status: "failed", questions_added: 0, error: String(err) });
    } finally {
      setMiningAll(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const usageBar = (used: number, limit: number, label: string) => {
    const pct = limit > 0 ? Math.min((used / limit) * 100, 100) : 0;
    return (
      <div className="mb-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{label}</span>
          <span>
            {used.toLocaleString()} / {limit.toLocaleString()}
          </span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${
              pct > 80 ? "bg-rose-500" : pct > 50 ? "bg-amber-500" : "bg-emerald-500"
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => onNavigate("dashboard")}
          className="text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-gray-800">Admin Panel</h1>
      </div>

      {/* Mining Result */}
      {lastResult && (
        <div
          className={`rounded-xl p-4 border ${
            lastResult.status === "completed"
              ? "bg-emerald-50 border-emerald-200"
              : "bg-rose-50 border-rose-200"
          }`}
        >
          <p className="font-medium">
            {lastResult.status === "completed"
              ? `Mining complete: ${lastResult.questions_added} questions added`
              : `Mining failed: ${lastResult.error || "Unknown error"}`}
          </p>
          {lastResult.subject && (
            <p className="text-sm text-gray-600 mt-1">
              Subject: {lastResult.subject}
            </p>
          )}
        </div>
      )}

      {/* Mining Controls */}
      <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Pickaxe className="w-5 h-5 text-indigo-600" />
            <h3 className="font-medium text-gray-700">Question Mining</h3>
          </div>
          <button
            onClick={handleMineAll}
            disabled={miningAll}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-50 flex items-center gap-2"
          >
            {miningAll ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Mining All...
              </>
            ) : (
              <>
                <Pickaxe className="w-4 h-4" /> Mine All Subjects
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {subjects.map((subject) => (
            <div
              key={subject.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <p className="font-medium text-sm text-gray-700">
                  {subject.name}
                </p>
                <p className="text-xs text-gray-500">
                  {subject.question_count} questions
                </p>
              </div>
              <button
                onClick={() => handleMineSubject(subject.id)}
                disabled={mining === subject.id}
                className="text-indigo-600 hover:bg-indigo-50 px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
              >
                {mining === subject.id ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  "Mine"
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* API Usage */}
      {apiUsage && (
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <h3 className="font-medium text-gray-700">
              API Usage (Today)
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                LLM APIs
              </h4>
              {usageBar(
                apiUsage.groq_tokens_used,
                apiUsage.groq_daily_limit,
                "Groq (tokens)"
              )}
              {usageBar(
                apiUsage.gemini_calls_used,
                apiUsage.gemini_daily_limit,
                "Gemini (calls)"
              )}
              {usageBar(
                apiUsage.mistral_tokens_used,
                apiUsage.mistral_daily_limit,
                "Mistral (tokens)"
              )}
            </div>
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                Search APIs
              </h4>
              {usageBar(
                apiUsage.tavily_calls_used,
                apiUsage.tavily_daily_limit,
                "Tavily (calls)"
              )}
              {usageBar(
                apiUsage.serper_calls_used,
                apiUsage.serper_daily_limit,
                "Serper (calls)"
              )}
            </div>
          </div>
        </div>
      )}

      {/* Mining Logs */}
      <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-indigo-600" />
          <h3 className="font-medium text-gray-700">Mining Logs</h3>
          <button
            onClick={loadData}
            className="ml-auto text-gray-400 hover:text-gray-600"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {logs.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">
            No mining logs yet. Trigger a mining job to get started.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Subject</th>
                  <th className="pb-2">Questions</th>
                  <th className="pb-2">API</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => {
                  const subjectName =
                    subjects.find((s) => s.id === log.subject_id)?.name ||
                    `Subject ${log.subject_id}`;
                  return (
                    <tr
                      key={log.id}
                      className="border-b border-gray-50 last:border-0"
                    >
                      <td className="py-2 text-gray-600">
                        {log.mined_date
                          ? new Date(log.mined_date).toLocaleDateString()
                          : "N/A"}
                      </td>
                      <td className="py-2 text-gray-700">{subjectName}</td>
                      <td className="py-2 font-medium">
                        +{log.questions_added}
                      </td>
                      <td className="py-2 text-gray-500">
                        {log.api_used || "N/A"}
                      </td>
                      <td className="py-2">
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            log.status === "completed"
                              ? "bg-emerald-50 text-emerald-700"
                              : log.status === "running"
                              ? "bg-blue-50 text-blue-700"
                              : log.status === "failed"
                              ? "bg-rose-50 text-rose-700"
                              : "bg-gray-50 text-gray-700"
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
