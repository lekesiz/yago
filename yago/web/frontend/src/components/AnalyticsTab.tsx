/**
 * YAGO v8.1 - Enhanced Analytics Tab Component
 * Production-ready analytics with real-time data aggregation
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

interface AnalyticsData {
  overview: {
    total_projects: number;
    completed: number;
    failed: number;
    in_progress: number;
    total_cost: number;
    total_files: number;
    total_lines: number;
    avg_duration_minutes: number;
  };
  ai_usage: {
    by_model: Array<{
      model: string;
      count: number;
      total_cost: number;
      total_lines: number;
    }>;
    by_strategy: Array<{
      strategy: string;
      count: number;
      success_rate: number;
    }>;
    by_provider: Array<{
      provider: string;
      requests: number;
      total_tokens: number;
      total_cost: number;
      avg_latency: number;
      success_rate: number;
    }>;
  };
  timeline: Array<{
    date: string;
    projects_created: number;
    projects_completed: number;
    cost: number;
    lines_of_code: number;
  }>;
  top_projects: Array<{
    id: string;
    name: string;
    lines_of_code: number;
    files_generated: number;
    status: string;
    cost: number;
  }>;
  range: string;
}

export const AnalyticsTab: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState('30d');

  const loadAnalytics = (selectedRange: string) => {
    setLoading(true);
    fetch(`http://localhost:8000/api/v1/analytics?range=${selectedRange}`)
      .then(r => r.json())
      .then(data => {
        setAnalytics(data);
        setRange(selectedRange);
      })
      .catch(() => toast.error('Failed to load analytics'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAnalytics(range);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!analytics) return null;

  const { overview, ai_usage, timeline, top_projects } = analytics;

  // Calculate percentages for AI usage
  const totalModelUsage = ai_usage.by_model.reduce((sum, m) => sum + m.count, 0);
  const modelsWithPercentage = ai_usage.by_model.map(m => ({
    ...m,
    percentage: totalModelUsage > 0 ? Math.round((m.count / totalModelUsage) * 100) : 0
  }));

  // Get last 14 days for timeline chart
  const recentTimeline = timeline.slice(-14);
  const maxProjects = Math.max(...recentTimeline.map(t => t.projects_created), 1);

  return (
    <div className="space-y-8 pb-8">
      {/* Header with Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
            Analytics Dashboard
          </h2>
          <p className="text-gray-400 mt-2">Real-time insights from your YAGO projects</p>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2 bg-white/5 backdrop-blur-sm rounded-lg p-1 border border-white/10">
          {[
            { label: '7 Days', value: '7d' },
            { label: '30 Days', value: '30d' },
            { label: 'All Time', value: 'all' }
          ].map(option => (
            <button
              key={option.value}
              onClick={() => loadAnalytics(option.value)}
              className={`px-4 py-2 rounded-md font-medium transition-all ${
                range === option.value
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Stats - Gradient Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: 'Total Projects',
            value: overview.total_projects,
            icon: '📦',
            gradient: 'from-blue-500 via-blue-600 to-cyan-500',
            subtitle: `${overview.completed} completed`
          },
          {
            label: 'Lines of Code',
            value: overview.total_lines.toLocaleString(),
            icon: '💻',
            gradient: 'from-purple-500 via-purple-600 to-pink-500',
            subtitle: `${overview.total_files} files`
          },
          {
            label: 'Total Cost',
            value: `$${overview.total_cost.toFixed(2)}`,
            icon: '💰',
            gradient: 'from-green-500 via-green-600 to-emerald-500',
            subtitle: 'AI usage cost'
          },
          {
            label: 'Avg Duration',
            value: `${overview.avg_duration_minutes.toFixed(1)}m`,
            icon: '⚡',
            gradient: 'from-yellow-500 via-orange-500 to-red-500',
            subtitle: 'Per project'
          }
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-r opacity-75 group-hover:opacity-100 blur-xl transition-opacity"
                 style={{ background: `linear-gradient(to right, var(--tw-gradient-stops))` }} />
            <div className={`relative bg-gradient-to-br ${stat.gradient} rounded-2xl p-6 border border-white/20 shadow-2xl`}>
              <div className="flex items-start justify-between mb-4">
                <div className="text-5xl filter drop-shadow-lg">{stat.icon}</div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white drop-shadow-lg">{stat.value}</div>
                  <div className="text-sm text-white/80 mt-1">{stat.subtitle}</div>
                </div>
              </div>
              <div className="text-white/90 font-medium text-sm">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'In Progress', value: overview.in_progress, color: 'text-yellow-400', icon: '🔄' },
          { label: 'Completed', value: overview.completed, color: 'text-green-400', icon: '✅' },
          { label: 'Failed', value: overview.failed, color: 'text-red-400', icon: '❌' }
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 + idx * 0.1 }}
            className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all"
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{stat.icon}</span>
              <span className="text-gray-400 text-sm">{stat.label}</span>
            </div>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
          </motion.div>
        ))}
      </div>

      {/* Activity Timeline - Bar Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
      >
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <span>📈</span>
          Activity Timeline (Last 14 Days)
        </h3>
        <div className="flex items-end justify-between h-48 gap-2">
          {recentTimeline.map((day, idx) => {
            const height = (day.projects_created / maxProjects) * 100;
            return (
              <motion.div
                key={day.date}
                initial={{ height: 0 }}
                animate={{ height: `${height}%` }}
                transition={{ delay: 0.8 + idx * 0.05, type: "spring" }}
                className="flex-1 group relative"
              >
                <div className="bg-gradient-to-t from-purple-500 via-pink-500 to-cyan-400 rounded-t-lg h-full min-h-[4px] hover:from-purple-400 hover:via-pink-400 hover:to-cyan-300 transition-all cursor-pointer" />

                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-black/90 text-white text-xs rounded-lg px-3 py-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                  <div className="font-bold">{new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                  <div>Projects: {day.projects_created}</div>
                  <div>Completed: {day.projects_completed}</div>
                  <div>Lines: {day.lines_of_code.toLocaleString()}</div>
                </div>
              </motion.div>
            );
          })}
        </div>
        <div className="flex justify-between mt-4 text-xs text-gray-500">
          <span>{new Date(recentTimeline[0]?.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
          <span>{new Date(recentTimeline[recentTimeline.length - 1]?.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
        </div>
      </motion.div>

      {/* AI Models Usage with Animated Progress Bars */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
      >
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <span>🤖</span>
          AI Model Usage
        </h3>
        <div className="space-y-4">
          {modelsWithPercentage.map((model, idx) => (
            <motion.div
              key={model.model}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1 + idx * 0.1 }}
              className="bg-black/20 rounded-xl p-4 hover:bg-black/30 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <span className="font-semibold text-white text-lg">{model.model}</span>
                  <span className="text-gray-400 text-sm ml-3">{model.count} projects</span>
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  {model.percentage}%
                </span>
              </div>

              {/* Animated Progress Bar */}
              <div className="relative w-full bg-gray-700/50 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${model.percentage}%` }}
                  transition={{ delay: 1.2 + idx * 0.1, duration: 0.8, ease: "easeOut" }}
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-400 rounded-full"
                />
              </div>

              <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                <div className="text-gray-400">
                  Lines: <span className="text-white font-medium">{model.total_lines.toLocaleString()}</span>
                </div>
                <div className="text-gray-400">
                  Cost: <span className="text-green-400 font-medium">${model.total_cost.toFixed(2)}</span>
                </div>
                <div className="text-gray-400">
                  Avg: <span className="text-cyan-400 font-medium">{Math.round(model.total_lines / model.count)} lines</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Strategy Distribution */}
      {ai_usage.by_strategy.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
        >
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span>🎯</span>
            Strategy Distribution
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {ai_usage.by_strategy.map((strategy, idx) => (
              <motion.div
                key={strategy.strategy}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.3 + idx * 0.1 }}
                className="bg-gradient-to-br from-white/10 to-white/5 rounded-xl p-6 border border-white/20 hover:border-purple-500/50 transition-all"
              >
                <div className="text-center">
                  <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                    {strategy.count}
                  </div>
                  <div className="text-white font-medium capitalize mb-2">{strategy.strategy}</div>
                  <div className="text-sm text-gray-400">
                    Success Rate: <span className="text-green-400 font-bold">{strategy.success_rate}%</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Top Projects Leaderboard */}
      {top_projects.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
        >
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span>🏆</span>
            Top Projects by Code Size
          </h3>
          <div className="space-y-3">
            {top_projects.map((project, idx) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.5 + idx * 0.1 }}
                className="flex items-center gap-4 bg-black/20 rounded-xl p-4 hover:bg-black/30 transition-all group"
              >
                <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-2xl font-bold text-white">
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white truncate group-hover:text-purple-400 transition-colors">
                    {project.name}
                  </div>
                  <div className="text-sm text-gray-400 flex items-center gap-4 mt-1">
                    <span>{project.lines_of_code.toLocaleString()} lines</span>
                    <span>{project.files_generated} files</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      project.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      project.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-400">${project.cost.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">cost</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};
