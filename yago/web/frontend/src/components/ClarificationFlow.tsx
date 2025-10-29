/**
 * YAGO v8.0 - Clarification Flow Container
 * Main orchestrator component for the entire clarification process
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';
import { useClarificationStore } from '../store/clarificationStore';
import { StartScreen } from './StartScreen';
import { CompletionScreen } from './CompletionScreen';
import { QuestionCard } from './QuestionCard';
import { ProgressBar } from './ProgressBar';
import { NavigationControls } from './NavigationControls';
import { Header } from './Header';
import { AgentSelection } from './AgentSelection';

type FlowStage = 'start' | 'clarifying' | 'completed' | 'agent-selection' | 'project-created';

export const ClarificationFlow: React.FC = () => {
  const [stage, setStage] = useState<FlowStage>('start');
  const [completionBrief, setCompletionBrief] = useState<any>(null);

  const {
    sessionId,
    currentQuestion,
    progress,
    answers,
    draftAnswers,
    loading,
    wsConnected,
    nextAvailable,
    previousAvailable,
    canFinishEarly,
    darkMode,
    startClarification,
    submitAnswer,
    navigateNext,
    navigatePrevious,
    completeClarification,
    disconnectWebSocket,
    toggleDarkMode,
    reset,
  } = useClarificationStore();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only handle shortcuts in clarifying stage
      if (stage !== 'clarifying') return;

      // Ctrl/Cmd + K: Skip question
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        handleSkip();
      }

      // Arrow Left: Previous question
      if (e.key === 'ArrowLeft' && !e.target || (e.target as HTMLElement).tagName !== 'INPUT') {
        e.preventDefault();
        handlePrevious();
      }

      // Arrow Right: Next question
      if (e.key === 'ArrowRight' && !e.target || (e.target as HTMLElement).tagName !== 'INPUT') {
        e.preventDefault();
        handleNext();
      }

      // Shift + Enter: Skip question
      if (e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        handleSkip();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [stage, currentQuestion]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  // Handle start clarification
  const handleStart = async (projectIdea: string, depth: 'minimal' | 'standard' | 'full') => {
    try {
      await startClarification({
        project_idea: projectIdea,
        depth,
        user_id: localStorage.getItem('yago_user_id') || undefined,
      });
      setStage('clarifying');
      toast.success('Clarification started! Let\'s build something amazing.');
    } catch (error) {
      console.error('Failed to start clarification:', error);
      toast.error('Failed to start clarification. Please try again.');
    }
  };

  // Handle answer submission
  const handleAnswer = async (answer: any) => {
    if (!currentQuestion) return;

    try {
      await submitAnswer(answer, false);
      toast.success('Answer saved!');
      // Check if this was the last question
      if (progress && progress.answered >= progress.total) {
        handleComplete();
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast.error('Failed to submit answer. Please try again.');
    }
  };

  // Handle skip
  const handleSkip = async () => {
    if (!currentQuestion) return;

    try {
      await submitAnswer(null, true);
      toast('Question skipped', { icon: '⏭️' });
      // Check if this was the last question
      if (progress && progress.answered >= progress.total) {
        handleComplete();
      }
    } catch (error) {
      console.error('Failed to skip question:', error);
      toast.error('Failed to skip question. Please try again.');
    }
  };

  // Handle navigation
  const handleNext = async () => {
    try {
      await navigateNext();
    } catch (error) {
      console.error('Failed to navigate:', error);
      toast.error('Failed to navigate. Please try again.');
    }
  };

  const handlePrevious = async () => {
    try {
      await navigatePrevious();
    } catch (error) {
      console.error('Failed to navigate:', error);
      toast.error('Failed to navigate. Please try again.');
    }
  };

  // Handle early finish
  const handleFinishEarly = async () => {
    if (!progress) return;

    // Confirm if user wants to finish early
    const confirm = window.confirm(
      `You've answered ${progress.answered} out of ${progress.total} questions. ` +
      `Are you sure you want to finish early?`
    );

    if (confirm) {
      handleComplete();
    }
  };

  // Handle completion
  const handleComplete = async () => {
    if (!sessionId) return;

    try {
      const brief = await completeClarification();
      setCompletionBrief(brief);
      setStage('completed');
      disconnectWebSocket();
      toast.success('🎉 Clarification completed successfully!');
    } catch (error) {
      console.error('Failed to complete clarification:', error);
      toast.error('Failed to complete clarification. Please try again.');
    }
  };

  // Handle start new project
  const handleStartNew = () => {
    reset();
    setStage('start');
    setCompletionBrief(null);
  };

  // Handle continue to agent selection
  const handleContinue = () => {
    console.log('Moving to agent selection with brief:', completionBrief);
    setStage('agent-selection');
  };

  // Handle agent selection complete
  const handleAgentSelectionComplete = async (config: any) => {
    console.log('Project configuration:', config);

    try {
      // Create project via API
      const response = await axios.post('http://localhost:8000/api/v1/projects', {
        brief: completionBrief,
        config: config
      });

      console.log('Project created:', response.data);
      toast.success(`🎉 Project created successfully! ID: ${response.data.project_id.slice(0, 8)}...`);
      setStage('project-created');
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project. Please try again.');
    }
  };

  // Handle back from agent selection
  const handleBackFromAgentSelection = () => {
    setStage('completed');
  };

  // Get project idea from session
  const getProjectIdea = () => {
    if (!sessionId) return undefined;
    // Project idea is stored in the brief or we can fetch it from the session
    return completionBrief?.project_idea || 'Your Project';
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
        <AnimatePresence mode="wait">
          {/* START SCREEN */}
          {stage === 'start' && (
            <motion.div
              key="start"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <StartScreen onStart={handleStart} loading={loading} />
            </motion.div>
          )}

          {/* CLARIFYING SCREEN */}
          {stage === 'clarifying' && (
            <motion.div
              key="clarifying"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Header */}
              <Header
                projectIdea={getProjectIdea()}
                darkMode={darkMode}
                onToggleDarkMode={toggleDarkMode}
              />

              <div className="container mx-auto px-4 py-8">
                {/* WebSocket Connection Status */}
                <div className="mb-4 flex items-center justify-center">
                  <div
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm ${
                      wsConnected
                        ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                        : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300'
                    }`}
                  >
                    <div
                      className={`w-2 h-2 rounded-full ${
                        wsConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
                      }`}
                    />
                    {wsConnected ? 'Connected' : 'Connecting...'}
                  </div>
                </div>

                {/* Progress Bar */}
                {progress && (
                  <div className="mb-8">
                    <ProgressBar progress={progress} />
                  </div>
                )}

                {/* Current Question */}
                {currentQuestion && (
                  <div className="mb-8">
                    <QuestionCard
                      question={currentQuestion}
                      onAnswer={handleAnswer}
                      initialValue={draftAnswers[currentQuestion.id] || answers[currentQuestion.id]}
                    />
                  </div>
                )}

                {/* Navigation Controls */}
                <NavigationControls
                  onNext={handleNext}
                  onPrevious={handlePrevious}
                  onSkip={handleSkip}
                  onFinish={handleFinishEarly}
                  canNext={nextAvailable}
                  canPrevious={previousAvailable}
                  canSkip={currentQuestion ? !currentQuestion.required : false}
                  canFinish={canFinishEarly}
                  loading={loading}
                />

                {/* Loading Overlay */}
                {loading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="fixed inset-0 bg-black/20 dark:bg-black/40 flex items-center justify-center z-50"
                  >
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 flex flex-col items-center gap-4">
                      <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                      <p className="text-gray-700 dark:text-gray-300 font-medium">
                        Processing...
                      </p>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}

          {/* COMPLETION SCREEN */}
          {stage === 'completed' && completionBrief && (
            <motion.div
              key="completed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <CompletionScreen
                brief={completionBrief}
                onStartNew={handleStartNew}
                onContinue={handleContinue}
              />
            </motion.div>
          )}

          {/* AGENT SELECTION SCREEN */}
          {stage === 'agent-selection' && completionBrief && (
            <motion.div
              key="agent-selection"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <AgentSelection
                brief={completionBrief}
                onComplete={handleAgentSelectionComplete}
                onBack={handleBackFromAgentSelection}
              />
            </motion.div>
          )}

          {/* PROJECT CREATED SCREEN */}
          {stage === 'project-created' && (
            <motion.div
              key="project-created"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800"
            >
              <div className="text-center p-8">
                <div className="text-8xl mb-6">🎉</div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                  Project Created!
                </h1>
                <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
                  Your AI agents are ready to start building.
                </p>
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={handleStartNew}
                    className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
                  >
                    ✨ Create Another Project
                  </button>
                  <button
                    onClick={() => setStage('start')}
                    className="px-8 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold rounded-lg transition"
                  >
                    🏠 Back to Dashboard
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ClarificationFlow;
