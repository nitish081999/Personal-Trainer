import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Target,
  ArrowLeft,
} from "lucide-react";
import { getUserAnalytics, getWeakTopics } from "@/lib/api";
import type { UserAnalytics, WeakTopic } from "@/types/api";

interface AnalyticsProps {
  userId: string;
  onNavigate: (page: string) => void;
}

export default function AnalyticsPage({ userId, onNavigate }: AnalyticsProps) {
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [weakTopics, setWeakTopics] = useState<WeakTopic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [ana, weak] = await Promise.all([
          getUserAnalytics(userId),
          getWeakTopics(userId),
        ]);
        setAnalytics(ana);
        setWeakTopics(weak);
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!analytics || analytics.total_attempts === 0) {
    return (
      <div className="text-center py-16">
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h2 className="text-lg font-medium text-gray-600">No data yet</h2>
        <p className="text-gray-400 mt-2">
          Start practicing to see your analytics!
        </p>
        <button
          onClick={() => onNavigate("quiz")}
          className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg"
        >
          Start Quiz
        </button>
      </div>
    );
  }

  const COLORS = [
    "#6366f1",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
  ];

  const subjectChartData = analytics.subjects.map((s) => ({
    name: s.subject_name.length > 10 ? s.subject_name.slice(0, 10) + "..." : s.subject_name,
    accuracy: Math.round(s.accuracy * 100),
    total: s.total,
    correct: s.correct,
  }));

  const pieData = [
    { name: "Correct", value: analytics.total_correct },
    { name: "Incorrect", value: analytics.total_attempts - analytics.total_correct },
  ];

  const accuracyTrend =
    analytics.recent_accuracy >= analytics.overall_accuracy ? "up" : "down";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => onNavigate("dashboard")}
          className="text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-gray-800">Your Analytics</h1>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p className="text-sm text-gray-500">Overall Accuracy</p>
          <p className="text-2xl font-bold text-gray-800">
            {(analytics.overall_accuracy * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p className="text-sm text-gray-500">Recent Accuracy</p>
          <div className="flex items-center gap-2">
            <p className="text-2xl font-bold text-gray-800">
              {(analytics.recent_accuracy * 100).toFixed(1)}%
            </p>
            {accuracyTrend === "up" ? (
              <TrendingUp className="w-5 h-5 text-emerald-500" />
            ) : (
              <TrendingDown className="w-5 h-5 text-rose-500" />
            )}
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p className="text-sm text-gray-500">Total Attempted</p>
          <p className="text-2xl font-bold text-gray-800">
            {analytics.total_attempts}
          </p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p className="text-sm text-gray-500">Avg. Time</p>
          <p className="text-2xl font-bold text-gray-800">
            {analytics.average_time.toFixed(1)}s
          </p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Subject-wise Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <h3 className="font-medium text-gray-700 mb-4">
            Subject-wise Accuracy
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={subjectChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" fontSize={12} />
              <YAxis domain={[0, 100]} fontSize={12} />
              <Tooltip
                formatter={(value: number) => [`${value}%`, "Accuracy"]}
              />
              <Bar dataKey="accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <h3 className="font-medium text-gray-700 mb-4">
            Correct vs Incorrect
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                <Cell fill="#10b981" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Weak Topics */}
      {weakTopics.length > 0 && (
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            <h3 className="font-medium text-gray-700">
              Weak Topics (Focus Areas)
            </h3>
          </div>
          <div className="space-y-3">
            {weakTopics.map((wt) => (
              <div
                key={wt.topic_id}
                className="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-100"
              >
                <div>
                  <p className="font-medium text-gray-700">{wt.topic_name}</p>
                  <p className="text-xs text-gray-500">{wt.subject_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-rose-600">
                    {(wt.accuracy * 100).toFixed(1)}% accuracy
                  </p>
                  <p className="text-xs text-gray-500">
                    Weakness: {(wt.weakness_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Subject Details */}
      <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
        <h3 className="font-medium text-gray-700 mb-4">
          Detailed Subject Breakdown
        </h3>
        <div className="space-y-4">
          {analytics.subjects.map((subject, sIdx) => (
            <div key={subject.subject_id} className="border-b border-gray-50 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-800">
                  {subject.subject_name}
                </h4>
                <span
                  className={`text-sm font-medium ${
                    subject.accuracy >= 0.7
                      ? "text-emerald-600"
                      : subject.accuracy >= 0.4
                      ? "text-amber-600"
                      : "text-rose-600"
                  }`}
                >
                  {(subject.accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-2">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${subject.accuracy * 100}%`,
                    backgroundColor: COLORS[sIdx % COLORS.length],
                  }}
                />
              </div>
              {subject.topics.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                  {subject.topics.map((topic) => (
                    <div
                      key={topic.topic_id}
                      className="text-xs px-2 py-1 bg-gray-50 rounded"
                    >
                      <span className="text-gray-600">{topic.topic_name}</span>
                      <span
                        className={`ml-1 font-medium ${
                          topic.accuracy >= 0.7
                            ? "text-emerald-600"
                            : "text-rose-600"
                        }`}
                      >
                        {(topic.accuracy * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
