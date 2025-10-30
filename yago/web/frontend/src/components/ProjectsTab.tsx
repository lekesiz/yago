/**
 * YAGO v8.0 - Projects Tab
 * View and manage all created projects
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import { CodePreview } from './CodePreview';
import { RealtimeProgress } from './RealtimeProgress';

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'creating' | 'in_progress' | 'paused' | 'completed' | 'failed';
  progress: number;
  primary_model: string;
  agent_role: string;
  strategy: string;
  temperature: number;
  max_tokens: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  cost_estimate: number;
  actual_cost: number;
  files_generated: number;
  lines_of_code: number;
  project_path?: string;
  errors: Array<{ timestamp: string; error: string }>;
  logs: Array<{ timestamp: string; log: string }>;
}

const statusColors = {
  creating: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50',
  in_progress: 'bg-blue-500/20 text-blue-300 border-blue-500/50',
  paused: 'bg-gray-500/20 text-gray-300 border-gray-500/50',
  completed: 'bg-green-500/20 text-green-300 border-green-500/50',
  failed: 'bg-red-500/20 text-red-300 border-red-500/50',
};

const statusIcons = {
  creating: '🔨',
  in_progress: '⚙️',
  paused: '⏸️',
  completed: '✅',
  failed: '❌',
};

export const ProjectsTab: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [previewProject, setPreviewProject] = useState<{ id: string; name: string } | null>(null);
  const [executingProject, setExecutingProject] = useState<{ id: string; name: string } | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/v1/projects');
      setProjects(response.data.projects || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
      setLoading(false);
    }
  };

  const deleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await axios.delete(`http://localhost:8000/api/v1/projects/${projectId}`);
      toast.success('Project deleted successfully');
      loadProjects();
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error('Failed to delete project');
    }
  };

  const startProject = async (projectId: string, projectName: string) => {
    try {
      // Show realtime progress modal
      setExecutingProject({ id: projectId, name: projectName });

      // Start execution
      await axios.post(`http://localhost:8000/api/v1/projects/${projectId}/execute`);

    } catch (error) {
      console.error('Failed to start project:', error);
      toast.error('Failed to start project');
      setExecutingProject(null);
    }
  };

  const pauseProject = async (projectId: string) => {
    try {
      await axios.post(`http://localhost:8000/api/v1/projects/${projectId}/pause`);
      toast.success('Project paused');
      loadProjects();
    } catch (error) {
      console.error('Failed to pause project:', error);
      toast.error('Failed to pause project');
    }
  };

  const resumeProject = async (projectId: string) => {
    try {
      await axios.post(`http://localhost:8000/api/v1/projects/${projectId}/resume`);
      toast.success('Project resumed');
      loadProjects();
    } catch (error) {
      console.error('Failed to resume project:', error);
      toast.error('Failed to resume project');
    }
  };

  const downloadProjectZip = async (projectId: string, projectName: string) => {
    try {
      toast.loading('Preparing download...');
      const response = await axios.get(
        `http://localhost:8000/api/v1/projects/${projectId}/download`,
        { responseType: 'blob' }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${projectName}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.dismiss();
      toast.success('Project downloaded successfully!');
    } catch (error) {
      console.error('Failed to download project:', error);
      toast.dismiss();
      toast.error('Failed to download project');
    }
  };

  const filteredProjects = projects
    .filter((p) => filterStatus === 'all' || p.status === filterStatus)
    .filter((p) =>
      searchQuery === '' ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const formatDuration = (startStr: string | null, endStr: string | null) => {
    if (!startStr) return 'Not started';
    const start = new Date(startStr);
    const end = endStr ? new Date(endStr) : new Date();
    const diff = end.getTime() - start.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    return `${minutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">🗂️ Projects</h2>
          <p className="text-gray-400 mt-1">Manage and track all your AI projects</p>
        </div>
        <button
          onClick={loadProjects}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition flex items-center gap-2"
        >
          <span>🔄</span>
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[
          { label: 'Total', count: projects.length, icon: '📊', color: 'from-blue-500 to-cyan-500' },
          { label: 'In Progress', count: projects.filter(p => p.status === 'in_progress').length, icon: '⚙️', color: 'from-blue-500 to-indigo-500' },
          { label: 'Completed', count: projects.filter(p => p.status === 'completed').length, icon: '✅', color: 'from-green-500 to-emerald-500' },
          { label: 'Paused', count: projects.filter(p => p.status === 'paused').length, icon: '⏸️', color: 'from-gray-500 to-slate-500' },
          { label: 'Failed', count: projects.filter(p => p.status === 'failed').length, icon: '❌', color: 'from-red-500 to-rose-500' },
        ].map((stat, idx) => (
          <div
            key={idx}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{stat.icon}</span>
              <div className={`text-2xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}>
                {stat.count}
              </div>
            </div>
            <div className="text-gray-400 text-sm">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1">
          <input
            type="text"
            placeholder="🔍 Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Status Filter */}
        <div className="flex gap-2 overflow-x-auto">
          {['all', 'creating', 'in_progress', 'paused', 'completed', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${
                filterStatus === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-gray-400 hover:bg-white/20'
              }`}
            >
              {status === 'all' ? 'All' : status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>

      {/* Projects List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading projects...</p>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-12 bg-white/5 rounded-xl border border-white/10">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-bold text-white mb-2">No Projects Found</h3>
          <p className="text-gray-400">
            {searchQuery || filterStatus !== 'all'
              ? 'Try adjusting your filters'
              : 'Create your first project to get started!'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProjects.map((project) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-purple-500/50 transition overflow-hidden"
            >
              {/* Project Header */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">{project.name}</h3>
                    <p className="text-gray-400 text-sm line-clamp-2">{project.description}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[project.status]}`}>
                    {statusIcons[project.status]} {project.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                {/* Progress Bar */}
                {project.status === 'in_progress' && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-400">Progress</span>
                      <span className="text-xs text-gray-400">{project.progress}%</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Project Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-gray-400">Model</div>
                    <div className="text-sm text-white font-medium">{project.primary_model}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Role</div>
                    <div className="text-sm text-white font-medium">{project.agent_role}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Cost</div>
                    <div className="text-sm text-white font-medium">${project.actual_cost.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Files</div>
                    <div className="text-sm text-white font-medium">{project.files_generated}</div>
                  </div>
                </div>

                {/* Timestamps */}
                <div className="text-xs text-gray-400 space-y-1 mb-4">
                  <div>Created: {formatDate(project.created_at)}</div>
                  {project.started_at && <div>Duration: {formatDuration(project.started_at, project.completed_at)}</div>}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedProject(project)}
                    className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition"
                  >
                    👁️ View Details
                  </button>

                  {project.status === 'completed' && (
                    <>
                      <button
                        onClick={() => setPreviewProject({ id: project.id, name: project.name })}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition"
                        title="Preview code in browser"
                      >
                        👁️ Preview
                      </button>
                      <button
                        onClick={() => downloadProjectZip(project.id, project.name)}
                        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white text-sm rounded-lg transition"
                        title="Download project as ZIP"
                      >
                        📦 Download
                      </button>
                    </>
                  )}

                  {project.status === 'creating' && (
                    <button
                      onClick={() => startProject(project.id, project.name)}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition"
                    >
                      ▶️ Start
                    </button>
                  )}

                  {project.status === 'in_progress' && (
                    <button
                      onClick={() => pauseProject(project.id)}
                      className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded-lg transition"
                    >
                      ⏸️ Pause
                    </button>
                  )}

                  {project.status === 'paused' && (
                    <button
                      onClick={() => resumeProject(project.id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition"
                    >
                      ▶️ Resume
                    </button>
                  )}

                  <button
                    onClick={() => deleteProject(project.id)}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Project Detail Modal */}
      <AnimatePresence>
        {selectedProject && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedProject(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 rounded-xl border border-white/20 max-w-4xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="sticky top-0 bg-gray-900 border-b border-white/10 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-white">{selectedProject.name}</h3>
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-medium border ${statusColors[selectedProject.status]}`}>
                      {statusIcons[selectedProject.status]} {selectedProject.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedProject(null)}
                    className="text-gray-400 hover:text-white transition"
                  >
                    ✕
                  </button>
                </div>
              </div>

              {/* Modal Content */}
              <div className="p-6 space-y-6">
                {/* Description */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-2">📝 Description</h4>
                  <p className="text-gray-400">{selectedProject.description}</p>
                </div>

                {/* Configuration */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">⚙️ Configuration</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Primary Model</div>
                      <div className="text-white font-medium">{selectedProject.primary_model}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Agent Role</div>
                      <div className="text-white font-medium">{selectedProject.agent_role}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Strategy</div>
                      <div className="text-white font-medium">{selectedProject.strategy}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Temperature</div>
                      <div className="text-white font-medium">{selectedProject.temperature}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Max Tokens</div>
                      <div className="text-white font-medium">{selectedProject.max_tokens}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="text-xs text-gray-400">Progress</div>
                      <div className="text-white font-medium">{selectedProject.progress}%</div>
                    </div>
                  </div>
                </div>

                {/* Metrics */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">📊 Metrics</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white/5 rounded-lg p-3 text-center">
                      <div className="text-2xl mb-1">💰</div>
                      <div className="text-xs text-gray-400">Cost</div>
                      <div className="text-lg text-white font-bold">${selectedProject.actual_cost.toFixed(2)}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 text-center">
                      <div className="text-2xl mb-1">📁</div>
                      <div className="text-xs text-gray-400">Files</div>
                      <div className="text-lg text-white font-bold">{selectedProject.files_generated}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 text-center">
                      <div className="text-2xl mb-1">💻</div>
                      <div className="text-xs text-gray-400">Lines of Code</div>
                      <div className="text-lg text-white font-bold">{selectedProject.lines_of_code}</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3 text-center">
                      <div className="text-2xl mb-1">⏱️</div>
                      <div className="text-xs text-gray-400">Duration</div>
                      <div className="text-lg text-white font-bold">
                        {formatDuration(selectedProject.started_at, selectedProject.completed_at)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Timestamps */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">🕐 Timeline</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Created:</span>
                      <span className="text-white">{formatDate(selectedProject.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Updated:</span>
                      <span className="text-white">{formatDate(selectedProject.updated_at)}</span>
                    </div>
                    {selectedProject.started_at && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Started:</span>
                        <span className="text-white">{formatDate(selectedProject.started_at)}</span>
                      </div>
                    )}
                    {selectedProject.completed_at && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Completed:</span>
                        <span className="text-white">{formatDate(selectedProject.completed_at)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Project Files */}
                {selectedProject.status === 'completed' && selectedProject.project_path && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">📦 Project Files</h4>
                    <div className="space-y-3">
                      <div className="bg-white/5 rounded-lg p-4">
                        <div className="text-xs text-gray-400 mb-2">Project Location</div>
                        <div className="text-sm text-white font-mono bg-black/30 px-3 py-2 rounded break-all">
                          {selectedProject.project_path}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => {
                            setPreviewProject({ id: selectedProject.id, name: selectedProject.name });
                            setSelectedProject(null);
                          }}
                          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition flex items-center justify-center gap-2"
                        >
                          👁️ Preview Code
                        </button>
                        <button
                          onClick={() => downloadProjectZip(selectedProject.id, selectedProject.name)}
                          className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-medium rounded-lg transition flex items-center justify-center gap-2"
                        >
                          📦 Download ZIP
                        </button>
                      </div>
                      <div className="text-xs text-gray-400 text-center">
                        {selectedProject.files_generated} files • {selectedProject.lines_of_code} lines of code
                      </div>
                    </div>
                  </div>
                )}

                {/* Errors */}
                {selectedProject.errors && selectedProject.errors.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">❌ Errors ({selectedProject.errors.length})</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedProject.errors.map((error, idx) => (
                        <div key={idx} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                          <div className="text-xs text-gray-400 mb-1">{formatDate(error.timestamp)}</div>
                          <div className="text-sm text-red-300">{error.error}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Logs */}
                {selectedProject.logs && selectedProject.logs.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">📋 Logs ({selectedProject.logs.length})</h4>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {selectedProject.logs.map((log, idx) => (
                        <div key={idx} className="bg-white/5 rounded-lg p-3">
                          <div className="text-xs text-gray-400 mb-1">{formatDate(log.timestamp)}</div>
                          <div className="text-sm text-gray-300 font-mono">{log.log}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Code Preview Modal */}
      <AnimatePresence>
        {previewProject && (
          <CodePreview
            projectId={previewProject.id}
            projectName={previewProject.name}
            onClose={() => setPreviewProject(null)}
          />
        )}
      </AnimatePresence>

      {/* Realtime Progress Modal */}
      <AnimatePresence>
        {executingProject && (
          <RealtimeProgress
            projectId={executingProject.id}
            projectName={executingProject.name}
            onComplete={(success, data) => {
              if (success) {
                toast.success('Project completed successfully!');
              }
              loadProjects();
            }}
            onClose={() => {
              setExecutingProject(null);
              loadProjects();
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProjectsTab;
