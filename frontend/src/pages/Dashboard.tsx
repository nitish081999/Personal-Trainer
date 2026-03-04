import { useEffect, useState } from "react";
import {
  BookOpen,
  Target,
  TrendingUp,
  Clock,
  ChevronRight,
  Brain,
  Zap,
} from "lucide-react";
import { getSubjects, getUserAnalytics, getQuestionCount } from "@/lib/api";
import type { Subject, UserAnalytics } from "@/types/api";

interface DashboardProps {
  userId: string;
  onNavigate: (page: string, data?: Record<string, unknown>) => void;
}

export default function Dashboard({ userId, onNavigate }: DashboardProps) {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [subs, ana, qCount] = await Promise.all([
          getSubjects(),
          getUserAnalytics(userId),
          getQuestionCount(),
        ]);
        setSubjects(subs);
        setAnalytics(ana);
        setTotalQuestions(qCount.count);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
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

  const subjectColors = [
    "bg-blue-500",
    "bg-emerald-500",
    "bg-amber-500",
    "bg-rose-500",
    "bg-purple-500",
    "bg-cyan-500",
  ];

  const subjectIcons = ["EN", "IP", "GE", "EC", "HI", "GK"];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">SSC Exam Prep Platform</h1>
        <p className="text-indigo-100">
          AI-powered preparation with adaptive learning and daily question
          mining
        </p>
        <div className="mt-4 flex gap-3">
          <button
            onClick={() => onNavigate("quiz")}
            className="bg-white text-indigo-600 px-4 py-2 rounded-lg font-medium hover:bg-indigo-50 transition flex items-center gap-2"
          >
            <Zap className="w-4 h-4" /> Start Quick Quiz
          </button>
          <button
            onClick={() => onNavigate("adaptive-quiz")}
            className="bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-400 transition flex items-center gap-2"
          >
            <Brain className="w-4 h-4" /> Adaptive Quiz
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <BookOpen className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Questions</p>
              <p className="text-xl font-bold">{totalQuestions}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-100 p-2 rounded-lg">
              <Target className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Attempted</p>
              <p className="text-xl font-bold">
                {analytics?.total_attempts || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="bg-amber-100 p-2 rounded-lg">
              <TrendingUp className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Accuracy</p>
              <p className="text-xl font-bold">
                {analytics
                  ? `${(analytics.overall_accuracy * 100).toFixed(1)}%`
                  : "N/A"}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg Time</p>
              <p className="text-xl font-bold">
                {analytics ? `${analytics.average_time.toFixed(1)}s` : "N/A"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Subject Cards */}
      <div>
        <h2 className="text-lg font-semibold mb-3 text-gray-800">Subjects</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((subject, index) => {
            const subjectAnalytics = analytics?.subjects.find(
              (s) => s.subject_id === subject.id
            );
            const accuracy = subjectAnalytics
              ? (subjectAnalytics.accuracy * 100).toFixed(1)
              : null;

            return (
              <div
                key={subject.id}
                onClick={() =>
                  onNavigate("quiz", { subjectId: subject.id })
                }
                className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition cursor-pointer group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`${subjectColors[index % 6]} w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm`}
                    >
                      {subjectIcons[index % 6]}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-800">
                        {subject.name}
                      </h3>
                      <p className="text-xs text-gray-500">
                        {subject.question_count} questions &middot;{" "}
                        {subject.topic_count} topics
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-indigo-500 transition" />
                </div>
                {accuracy && (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-500">Accuracy</span>
                      <span className="font-medium text-gray-700">
                        {accuracy}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          parseFloat(accuracy) >= 70
                            ? "bg-emerald-500"
                            : parseFloat(accuracy) >= 40
                            ? "bg-amber-500"
                            : "bg-rose-500"
                        }`}
                        style={{ width: `${accuracy}%` }}
                      />
                    </div>
                  </div>
                )}
                {subjectAnalytics && (
                  <p className="text-xs text-gray-400 mt-2">
                    {subjectAnalytics.correct}/{subjectAnalytics.total} correct
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
