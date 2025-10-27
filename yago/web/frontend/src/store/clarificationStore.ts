/**
 * YAGO v7.1 - Zustand Store for Clarification State
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  QuestionUI,
  ClarificationProgress,
  StartClarificationRequest,
  AnswerRequest,
} from '../types/clarification';
import clarificationApi from '../services/clarificationApi';

interface ClarificationState {
  // Session data
  sessionId: string | null;
  projectIdea: string;
  depth: 'minimal' | 'standard' | 'full';

  // Current state
  currentQuestion: QuestionUI | null;
  progress: ClarificationProgress | null;
  answers: Record<string, any>;
  draftAnswers: Record<string, any>;

  // UI state
  loading: boolean;
  error: string | null;
  canSkip: boolean;
  canFinishEarly: boolean;
  nextAvailable: boolean;
  previousAvailable: boolean;

  // WebSocket
  wsConnected: boolean;
  ws: WebSocket | null;

  // Theme
  darkMode: boolean;

  // Actions
  startClarification: (request: StartClarificationRequest) => Promise<void>;
  submitAnswer: (answer: any, skip?: boolean) => Promise<void>;
  navigateNext: () => Promise<void>;
  navigatePrevious: () => Promise<void>;
  updateDraft: (questionId: string, value: any) => void;
  saveDraft: () => Promise<void>;
  completeClarification: () => Promise<any>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  toggleDarkMode: () => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  projectIdea: '',
  depth: 'standard' as const,
  currentQuestion: null,
  progress: null,
  answers: {},
  draftAnswers: {},
  loading: false,
  error: null,
  canSkip: false,
  canFinishEarly: false,
  nextAvailable: false,
  previousAvailable: false,
  wsConnected: false,
  ws: null,
  darkMode: false,
};

export const useClarificationStore = create<ClarificationState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        startClarification: async (request: StartClarificationRequest) => {
          set({ loading: true, error: null, projectIdea: request.project_idea, depth: request.depth });

          try {
            const response = await clarificationApi.start(request);
            set({
              sessionId: response.session_id,
              currentQuestion: response.current_question,
              progress: response.progress,
              canSkip: response.can_skip,
              canFinishEarly: response.can_finish_early,
              nextAvailable: response.next_available,
              previousAvailable: response.previous_available,
              loading: false,
            });

            // Connect WebSocket
            get().connectWebSocket();
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || 'Failed to start clarification',
              loading: false,
            });
          }
        },

        submitAnswer: async (answer: any, skip = false) => {
          const { sessionId, currentQuestion, answers } = get();
          if (!sessionId) return;

          set({ loading: true, error: null });

          try {
            const request: AnswerRequest = { answer, skip };
            const response = await clarificationApi.submitAnswer(sessionId, request);

            // Update answers
            const newAnswers = { ...answers };
            if (currentQuestion && !skip) {
              newAnswers[currentQuestion.id] = answer;
            }

            set({
              currentQuestion: response.current_question,
              progress: response.progress,
              answers: newAnswers,
              draftAnswers: {},
              canSkip: response.can_skip,
              canFinishEarly: response.can_finish_early,
              nextAvailable: response.next_available,
              previousAvailable: response.previous_available,
              loading: false,
            });
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || 'Failed to submit answer',
              loading: false,
            });
          }
        },

        navigateNext: async () => {
          const { sessionId } = get();
          if (!sessionId) return;

          set({ loading: true, error: null });

          try {
            const response = await clarificationApi.navigate(sessionId, 'next');
            set({
              currentQuestion: response.current_question,
              progress: response.progress,
              canSkip: response.can_skip,
              canFinishEarly: response.can_finish_early,
              nextAvailable: response.next_available,
              previousAvailable: response.previous_available,
              loading: false,
            });
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || 'Failed to navigate',
              loading: false,
            });
          }
        },

        navigatePrevious: async () => {
          const { sessionId } = get();
          if (!sessionId) return;

          set({ loading: true, error: null });

          try {
            const response = await clarificationApi.navigate(sessionId, 'previous');
            set({
              currentQuestion: response.current_question,
              progress: response.progress,
              canSkip: response.can_skip,
              canFinishEarly: response.can_finish_early,
              nextAvailable: response.next_available,
              previousAvailable: response.previous_available,
              loading: false,
            });
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || 'Failed to navigate',
              loading: false,
            });
          }
        },

        updateDraft: (questionId: string, value: any) => {
          const { draftAnswers } = get();
          set({
            draftAnswers: { ...draftAnswers, [questionId]: value },
          });
        },

        saveDraft: async () => {
          const { sessionId, draftAnswers, answers } = get();
          if (!sessionId || Object.keys(draftAnswers).length === 0) return;

          try {
            const allAnswers = { ...answers, ...draftAnswers };
            await clarificationApi.updateDraft(sessionId, { answers: allAnswers });
          } catch (error) {
            console.error('Failed to save draft:', error);
          }
        },

        completeClarification: async () => {
          const { sessionId } = get();
          if (!sessionId) return null;

          set({ loading: true, error: null });

          try {
            const result = await clarificationApi.complete(sessionId);
            get().disconnectWebSocket();
            return result.brief;
          } catch (error: any) {
            set({
              error: error.response?.data?.detail || 'Failed to complete clarification',
              loading: false,
            });
            return null;
          }
        },

        connectWebSocket: () => {
          const { sessionId, ws } = get();
          if (!sessionId || ws) return;

          const wsUrl = `ws://localhost:8000/ws/${sessionId}`;
          const websocket = new WebSocket(wsUrl);

          websocket.onopen = () => {
            console.log('WebSocket connected');
            set({ wsConnected: true });
          };

          websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);

            if (message.type === 'progress_update') {
              // Update progress from WebSocket
              const { progress } = get();
              if (progress) {
                set({
                  progress: {
                    ...progress,
                    answered: message.data.answered,
                    total: message.data.total,
                    percentage: (message.data.answered / message.data.total) * 100,
                  },
                });
              }
            } else if (message.type === 'notification') {
              // Handle notifications (can be integrated with toast)
              console.log('Notification:', message.message);
            }
          };

          websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            set({ wsConnected: false });
          };

          websocket.onclose = () => {
            console.log('WebSocket disconnected');
            set({ wsConnected: false, ws: null });
          };

          set({ ws: websocket });

          // Send ping every 30 seconds to keep connection alive
          const pingInterval = setInterval(() => {
            if (websocket.readyState === WebSocket.OPEN) {
              websocket.send(JSON.stringify({ type: 'ping' }));
            }
          }, 30000);

          // Cleanup on disconnect
          websocket.addEventListener('close', () => {
            clearInterval(pingInterval);
          });
        },

        disconnectWebSocket: () => {
          const { ws } = get();
          if (ws) {
            ws.close();
            set({ ws: null, wsConnected: false });
          }
        },

        toggleDarkMode: () => {
          const { darkMode } = get();
          set({ darkMode: !darkMode });

          // Update document class
          if (!darkMode) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        },

        reset: () => {
          get().disconnectWebSocket();
          set(initialState);
        },
      }),
      {
        name: 'yago-clarification-storage',
        partialize: (state) => ({
          darkMode: state.darkMode,
          // Only persist dark mode preference
        }),
      }
    )
  )
);

export default useClarificationStore;
