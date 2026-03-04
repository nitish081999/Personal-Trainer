export interface Subject {
  id: number;
  name: string;
  topic_count: number;
  question_count: number;
}

export interface Topic {
  id: number;
  subject_id: number;
  name: string;
  question_count: number;
}

export interface Question {
  id: number;
  subject_id: number;
  topic_id: number | null;
  question_text: string;
  options: string[];
  correct_index: number;
  explanation: string | null;
  difficulty: string;
  source: string | null;
  created_at: string | null;
}

export interface QuestionBrief {
  id: number;
  subject_id: number;
  topic_id: number | null;
  question_text: string;
  options: string[];
  difficulty: string;
}

export interface AttemptCreate {
  user_id: string;
  question_id: number;
  selected_option: number;
  time_taken: number | null;
}

export interface AttemptResult {
  is_correct: boolean;
  correct_index: number;
  explanation: string | null;
  attempt: {
    id: number;
    user_id: string;
    question_id: number;
    selected_option: number;
    is_correct: boolean;
    time_taken: number | null;
    attempt_date: string | null;
  };
}

export interface TopicAccuracy {
  topic_id: number;
  topic_name: string;
  total: number;
  correct: number;
  accuracy: number;
}

export interface SubjectAccuracy {
  subject_id: number;
  subject_name: string;
  total: number;
  correct: number;
  accuracy: number;
  topics: TopicAccuracy[];
}

export interface UserAnalytics {
  user_id: string;
  total_attempts: number;
  total_correct: number;
  overall_accuracy: number;
  recent_accuracy: number;
  average_time: number;
  subjects: SubjectAccuracy[];
}

export interface WeakTopic {
  topic_id: number;
  topic_name: string;
  subject_name: string;
  weakness_score: number;
  accuracy: number;
}

export interface AdaptiveQuizResponse {
  questions: QuestionBrief[];
  focus_areas: string[];
}

export interface MiningLog {
  id: number;
  subject_id: number;
  questions_added: number;
  api_used: string | null;
  tokens_used: number;
  status: string;
  mined_date: string | null;
}

export interface APIUsage {
  groq_tokens_used: number;
  groq_daily_limit: number;
  gemini_calls_used: number;
  gemini_daily_limit: number;
  mistral_tokens_used: number;
  mistral_daily_limit: number;
  tavily_calls_used: number;
  tavily_daily_limit: number;
  serper_calls_used: number;
  serper_daily_limit: number;
}

export interface MiningResult {
  subject?: string;
  topic?: string;
  questions_added: number;
  total_found?: number;
  apis_used?: string[];
  status: string;
  error?: string;
}
