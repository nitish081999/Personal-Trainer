import { useEffect, useState, useRef } from "react";
import {
  CheckCircle,
  XCircle,
  Clock,
  ChevronRight,
  AlertCircle,
  ArrowLeft,
} from "lucide-react";
import {
  getRandomQuestions,
  getAdaptiveQuiz,
  recordAttempt,
  getQuestion,
} from "@/lib/api";
import type { QuestionBrief, AttemptResult } from "@/types/api";

interface QuizProps {
  userId: string;
  subjectId?: number;
  adaptive?: boolean;
  onNavigate: (page: string) => void;
}

interface QuizState {
  questions: QuestionBrief[];
  currentIndex: number;
  selectedOption: number | null;
  result: AttemptResult | null;
  score: number;
  totalAnswered: number;
  showExplanation: boolean;
  timer: number;
  focusAreas: string[];
  finished: boolean;
}

export default function Quiz({
  userId,
  subjectId,
  adaptive,
  onNavigate,
}: QuizProps) {
  const [state, setState] = useState<QuizState>({
    questions: [],
    currentIndex: 0,
    selectedOption: null,
    result: null,
    score: 0,
    totalAnswered: 0,
    showExplanation: false,
    timer: 0,
    focusAreas: [],
    finished: false,
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    async function loadQuestions() {
      try {
        if (adaptive) {
          const quiz = await getAdaptiveQuiz(userId, 20);
          setState((s) => ({
            ...s,
            questions: quiz.questions,
            focusAreas: quiz.focus_areas,
          }));
        } else {
          const questions = await getRandomQuestions({
            subject_id: subjectId,
            count: 20,
          });
          setState((s) => ({ ...s, questions }));
        }
      } catch (err) {
        console.error("Failed to load questions:", err);
      } finally {
        setLoading(false);
      }
    }
    loadQuestions();
  }, [userId, subjectId, adaptive]);

  // Timer
  useEffect(() => {
    if (!loading && !state.finished && !state.result) {
      timerRef.current = setInterval(() => {
        setState((s) => ({ ...s, timer: s.timer + 1 }));
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [loading, state.finished, state.result]);

  const currentQuestion = state.questions[state.currentIndex];

  const handleSelectOption = (index: number) => {
    if (state.result) return; // Already answered
    setState((s) => ({ ...s, selectedOption: index }));
  };

  const handleSubmitAnswer = async () => {
    if (state.selectedOption === null || !currentQuestion) return;
    setSubmitting(true);

    // Stop timer
    if (timerRef.current) clearInterval(timerRef.current);

    try {
      const result = await recordAttempt({
        user_id: userId,
        question_id: currentQuestion.id,
        selected_option: state.selectedOption,
        time_taken: state.timer,
      });

      // Get full question for explanation
      const fullQuestion = await getQuestion(currentQuestion.id);

      setState((s) => ({
        ...s,
        result: { ...result, explanation: fullQuestion.explanation },
        score: s.score + (result.is_correct ? 1 : 0),
        totalAnswered: s.totalAnswered + 1,
        showExplanation: true,
      }));
    } catch (err) {
      console.error("Failed to submit answer:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (state.currentIndex >= state.questions.length - 1) {
      setState((s) => ({ ...s, finished: true }));
      return;
    }

    setState((s) => ({
      ...s,
      currentIndex: s.currentIndex + 1,
      selectedOption: null,
      result: null,
      showExplanation: false,
      timer: 0,
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (state.questions.length === 0) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h2 className="text-lg font-medium text-gray-600">
          No questions available
        </h2>
        <p className="text-gray-400 mt-2">
          Try mining some questions first or select a different subject.
        </p>
        <button
          onClick={() => onNavigate("dashboard")}
          className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  // Quiz Results Screen
  if (state.finished) {
    const pct =
      state.totalAnswered > 0
        ? ((state.score / state.totalAnswered) * 100).toFixed(1)
        : "0";
    return (
      <div className="max-w-lg mx-auto text-center py-10">
        <div
          className={`w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center text-white text-3xl font-bold ${
            parseFloat(pct) >= 70
              ? "bg-emerald-500"
              : parseFloat(pct) >= 40
              ? "bg-amber-500"
              : "bg-rose-500"
          }`}
        >
          {pct}%
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Quiz Complete!
        </h2>
        <p className="text-gray-500 mb-6">
          You got {state.score} out of {state.totalAnswered} questions correct
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => onNavigate("dashboard")}
            className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition"
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate("analytics")}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
          >
            View Analytics
          </button>
        </div>
      </div>
    );
  }

  const progress =
    ((state.currentIndex + 1) / state.questions.length) * 100;
  const difficultyColor =
    currentQuestion.difficulty === "easy"
      ? "text-emerald-600 bg-emerald-50"
      : currentQuestion.difficulty === "hard"
      ? "text-rose-600 bg-rose-50"
      : "text-amber-600 bg-amber-50";

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => onNavigate("dashboard")}
          className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="flex items-center gap-4">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${difficultyColor}`}>
            {currentQuestion.difficulty}
          </span>
          <div className="flex items-center gap-1 text-gray-500">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-mono">{state.timer}s</span>
          </div>
        </div>
      </div>

      {/* Focus Areas Banner */}
      {adaptive && state.focusAreas.length > 0 && state.currentIndex === 0 && (
        <div className="bg-purple-50 border border-purple-100 rounded-lg p-3 mb-4">
          <p className="text-xs text-purple-700 font-medium">
            Focus areas: {state.focusAreas.join(", ")}
          </p>
        </div>
      )}

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>
            Question {state.currentIndex + 1} of {state.questions.length}
          </span>
          <span>
            Score: {state.score}/{state.totalAnswered}
          </span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm mb-4">
        <h2 className="text-lg font-medium text-gray-800 mb-6">
          {currentQuestion.question_text}
        </h2>

        {/* Options */}
        <div className="space-y-3">
          {currentQuestion.options.map((option, index) => {
            let optionStyle =
              "border-gray-200 hover:border-indigo-300 hover:bg-indigo-50";

            if (state.result) {
              if (index === state.result.correct_index) {
                optionStyle = "border-emerald-500 bg-emerald-50";
              } else if (
                index === state.selectedOption &&
                !state.result.is_correct
              ) {
                optionStyle = "border-rose-500 bg-rose-50";
              } else {
                optionStyle = "border-gray-100 opacity-60";
              }
            } else if (state.selectedOption === index) {
              optionStyle = "border-indigo-500 bg-indigo-50";
            }

            return (
              <button
                key={index}
                onClick={() => handleSelectOption(index)}
                disabled={!!state.result}
                className={`w-full text-left p-4 rounded-lg border-2 transition ${optionStyle}`}
              >
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center text-sm font-medium shrink-0">
                    {String.fromCharCode(65 + index)}
                  </span>
                  <span className="text-gray-700">{option}</span>
                  {state.result && index === state.result.correct_index && (
                    <CheckCircle className="w-5 h-5 text-emerald-500 ml-auto shrink-0" />
                  )}
                  {state.result &&
                    index === state.selectedOption &&
                    !state.result.is_correct && (
                      <XCircle className="w-5 h-5 text-rose-500 ml-auto shrink-0" />
                    )}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Explanation */}
      {state.showExplanation && state.result?.explanation && (
        <div
          className={`rounded-xl p-4 mb-4 border ${
            state.result.is_correct
              ? "bg-emerald-50 border-emerald-200"
              : "bg-rose-50 border-rose-200"
          }`}
        >
          <h3
            className={`font-medium mb-1 ${
              state.result.is_correct ? "text-emerald-700" : "text-rose-700"
            }`}
          >
            {state.result.is_correct ? "Correct!" : "Incorrect"}
          </h3>
          <p className="text-sm text-gray-700">{state.result.explanation}</p>
        </div>
      )}

      {/* Action Button */}
      <div className="flex justify-end">
        {!state.result ? (
          <button
            onClick={handleSubmitAnswer}
            disabled={state.selectedOption === null || submitting}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {submitting ? "Checking..." : "Submit Answer"}
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition flex items-center gap-2"
          >
            {state.currentIndex >= state.questions.length - 1
              ? "Finish Quiz"
              : "Next Question"}
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
