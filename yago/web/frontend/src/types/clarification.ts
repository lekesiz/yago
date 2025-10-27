/**
 * YAGO v7.1 - TypeScript Types for Clarification UI
 */

export type QuestionType = 'text' | 'select' | 'multiselect' | 'checkbox' | 'slider';

export type QuestionCategory = 'basic' | 'technical' | 'infrastructure' | 'security' | 'quality';

export interface QuestionUI {
  id: string;
  text: string;
  category: QuestionCategory;
  type: QuestionType;
  options?: string[];
  placeholder?: string;
  required: boolean;
  hint?: string;
  example?: string;
  min_value?: number;
  max_value?: number;
  default?: any;
}

export interface ClarificationProgress {
  answered: number;
  total: number;
  percentage: number;
  category_progress: Record<string, string>;
  estimated_time_remaining: number;
}

export interface ClarificationResponse {
  session_id: string;
  current_question: QuestionUI | null;
  progress: ClarificationProgress;
  can_skip: boolean;
  can_finish_early: boolean;
  next_available: boolean;
  previous_available: boolean;
}

export interface StartClarificationRequest {
  project_idea: string;
  depth: 'minimal' | 'standard' | 'full';
  user_id?: string;
}

export interface AnswerRequest {
  answer: any;
  skip: boolean;
}

export interface DraftUpdate {
  answers: Record<string, any>;
}

export interface NotificationMessage {
  type: 'notification';
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
}

export interface ProgressUpdate {
  type: 'progress_update';
  data: {
    answered: number;
    total: number;
  };
}

export type WebSocketMessage = NotificationMessage | ProgressUpdate;
