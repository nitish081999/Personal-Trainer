import type {
  Subject,
  Topic,
  Question,
  QuestionBrief,
  AttemptCreate,
  AttemptResult,
  UserAnalytics,
  WeakTopic,
  AdaptiveQuizResponse,
  MiningLog,
  APIUsage,
  MiningResult,
} from "@/types/api";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_URL}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`);
  }
  return resp.json();
}

// Subjects
export const getSubjects = () => fetchJSON<Subject[]>("/subjects");
export const getTopics = (subjectId: number) =>
  fetchJSON<Topic[]>(`/subjects/${subjectId}/topics`);

// Questions
export const getQuestions = (params?: {
  subject_id?: number;
  topic_id?: number;
  difficulty?: string;
  limit?: number;
  offset?: number;
}) => {
  const search = new URLSearchParams();
  if (params?.subject_id) search.set("subject_id", String(params.subject_id));
  if (params?.topic_id) search.set("topic_id", String(params.topic_id));
  if (params?.difficulty) search.set("difficulty", params.difficulty);
  if (params?.limit) search.set("limit", String(params.limit));
  if (params?.offset) search.set("offset", String(params.offset));
  return fetchJSON<Question[]>(`/questions?${search.toString()}`);
};

export const getRandomQuestions = (params?: {
  subject_id?: number;
  count?: number;
}) => {
  const search = new URLSearchParams();
  if (params?.subject_id) search.set("subject_id", String(params.subject_id));
  if (params?.count) search.set("count", String(params.count));
  return fetchJSON<QuestionBrief[]>(`/questions/random?${search.toString()}`);
};

export const getQuestionCount = (subjectId?: number) => {
  const search = subjectId ? `?subject_id=${subjectId}` : "";
  return fetchJSON<{ count: number }>(`/questions/count${search}`);
};

export const getQuestion = (id: number) =>
  fetchJSON<Question>(`/questions/${id}`);

// Attempts
export const recordAttempt = (data: AttemptCreate) =>
  fetchJSON<AttemptResult>("/attempts", {
    method: "POST",
    body: JSON.stringify(data),
  });

// Analytics
export const getUserAnalytics = (userId: string) =>
  fetchJSON<UserAnalytics>(`/analytics/${userId}`);

export const getWeakTopics = (userId: string) =>
  fetchJSON<WeakTopic[]>(`/analytics/${userId}/weak-topics`);

// Quiz
export const getAdaptiveQuiz = (userId: string, count: number = 20) =>
  fetchJSON<AdaptiveQuizResponse>("/quiz/adaptive", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, count, focus_weak: true }),
  });

// Mining
export const triggerMining = (subjectId: number, count: number = 20) =>
  fetchJSON<MiningResult>("/mining/trigger", {
    method: "POST",
    body: JSON.stringify({ subject_id: subjectId, count }),
  });

export const triggerMiningAll = (countPerSubject: number = 20) =>
  fetchJSON<{ results: MiningResult[] }>(
    `/mining/trigger-all?count_per_subject=${countPerSubject}`,
    { method: "POST" }
  );

export const getMiningLogs = (params?: {
  subject_id?: number;
  limit?: number;
}) => {
  const search = new URLSearchParams();
  if (params?.subject_id) search.set("subject_id", String(params.subject_id));
  if (params?.limit) search.set("limit", String(params.limit));
  return fetchJSON<MiningLog[]>(`/mining/logs?${search.toString()}`);
};

export const getAPIUsage = () => fetchJSON<APIUsage>("/mining/api-usage");
