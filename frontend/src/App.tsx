import { useState } from "react";
import {
  LayoutDashboard,
  BookOpen,
  BarChart3,
  Settings,
  Brain,
} from "lucide-react";
import Dashboard from "@/pages/Dashboard";
import Quiz from "@/pages/Quiz";
import AnalyticsPage from "@/pages/Analytics";
import AdminPage from "@/pages/Admin";

const USER_ID = "default_user";

type Page = "dashboard" | "quiz" | "adaptive-quiz" | "analytics" | "admin";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [quizSubjectId, setQuizSubjectId] = useState<number | undefined>();

  const handleNavigate = (page: string, data?: Record<string, unknown>) => {
    if (page === "quiz" && data?.subjectId) {
      setQuizSubjectId(data.subjectId as number);
    } else if (page === "quiz") {
      setQuizSubjectId(undefined);
    }
    setCurrentPage(page as Page);
  };

  const navItems: { id: Page; label: string; icon: typeof LayoutDashboard }[] = [
    { id: "dashboard", label: "Home", icon: LayoutDashboard },
    { id: "quiz", label: "Quiz", icon: BookOpen },
    { id: "adaptive-quiz", label: "Smart Quiz", icon: Brain },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "admin", label: "Admin", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Nav */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <div className="bg-indigo-600 w-8 h-8 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-gray-800">SSC Prep AI</span>
            </div>
            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavigate(item.id)}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
                      isActive
                        ? "bg-indigo-50 text-indigo-600"
                        : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        {currentPage === "dashboard" && (
          <Dashboard userId={USER_ID} onNavigate={handleNavigate} />
        )}
        {currentPage === "quiz" && (
          <Quiz
            key={`quiz-${quizSubjectId || "all"}-${Date.now()}`}
            userId={USER_ID}
            subjectId={quizSubjectId}
            onNavigate={handleNavigate}
          />
        )}
        {currentPage === "adaptive-quiz" && (
          <Quiz
            key={`adaptive-${Date.now()}`}
            userId={USER_ID}
            adaptive
            onNavigate={handleNavigate}
          />
        )}
        {currentPage === "analytics" && (
          <AnalyticsPage userId={USER_ID} onNavigate={handleNavigate} />
        )}
        {currentPage === "admin" && (
          <AdminPage onNavigate={handleNavigate} />
        )}
      </main>
    </div>
  );
}

export default App;
