/**
 * YAGO v8.2 - Enterprise Dashboard Component
 * Comprehensive enterprise features: Git Analysis, Code Refactoring, Doc Compliance, Auto Documentation
 */
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import axios from 'axios';

// API Base URL
const API_BASE = 'http://localhost:8000/api/v1/enterprise';

// TypeScript Interfaces
interface GitAnalysisResult {
  completion_score: number;
  todo_count: number;
  incomplete_features: number;
  language_breakdown: { [key: string]: number };
  git_stats: {
    total_commits: number;
    contributors: number;
    last_commit: string;
  };
  recommendations: string[];
}

interface RefactoringResult {
  total_issues: number;
  dead_code_count: number;
  duplicates_count: number;
  high_complexity_functions: number;
  refactoring_plan: Array<{
    priority: string;
    issue: string;
    file: string;
    suggestion: string;
  }>;
  potential_loc_savings: number;
}

interface ComplianceResult {
  compliance_score: number;
  missing_implementations: string[];
  undocumented_features: string[];
  compliance_report: {
    total_features: number;
    documented: number;
    implemented: number;
    missing: number;
  };
}

interface DocumentationResult {
  files_generated: number;
  documentation_types: string[];
  generated_files: Array<{
    name: string;
    path: string;
    size: string;
    download_url: string;
  }>;
}

export const EnterpriseDashboard: React.FC = () => {
  // State for Git Analysis
  const [gitUrl, setGitUrl] = useState('');
  const [gitLoading, setGitLoading] = useState(false);
  const [gitResult, setGitResult] = useState<GitAnalysisResult | null>(null);

  // State for Code Refactoring
  const [refactorPath, setRefactorPath] = useState('');
  const [refactorLoading, setRefactorLoading] = useState(false);
  const [refactorResult, setRefactorResult] = useState<RefactoringResult | null>(null);

  // State for Documentation Compliance
  const [compliancePath, setCompliancePath] = useState('');
  const [complianceDocsPath, setComplianceDocsPath] = useState('');
  const [complianceLoading, setComplianceLoading] = useState(false);
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);

  // State for Auto Documentation
  const [docsProjectPath, setDocsProjectPath] = useState('');
  const [docsLoading, setDocsLoading] = useState(false);
  const [docsResult, setDocsResult] = useState<DocumentationResult | null>(null);

  // Git Project Analysis Handler
  const handleGitAnalysis = async () => {
    if (!gitUrl.trim()) {
      toast.error('Please enter a Git URL');
      return;
    }

    setGitLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/analyze-git`, { git_url: gitUrl });
      setGitResult(response.data);
      toast.success('Git analysis completed!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Git analysis failed');
      console.error('Git analysis error:', error);
    } finally {
      setGitLoading(false);
    }
  };

  // Code Refactoring Handler
  const handleRefactoring = async () => {
    if (!refactorPath.trim()) {
      toast.error('Please enter a project path');
      return;
    }

    setRefactorLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/refactor-project`, { project_path: refactorPath });
      setRefactorResult(response.data);
      toast.success('Code refactoring analysis completed!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Refactoring analysis failed');
      console.error('Refactoring error:', error);
    } finally {
      setRefactorLoading(false);
    }
  };

  // Documentation Compliance Handler
  const handleCompliance = async () => {
    if (!compliancePath.trim()) {
      toast.error('Please enter a project path');
      return;
    }

    setComplianceLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/check-compliance`, {
        project_path: compliancePath,
        docs_path: complianceDocsPath || undefined
      });
      setComplianceResult(response.data);
      toast.success('Compliance check completed!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Compliance check failed');
      console.error('Compliance error:', error);
    } finally {
      setComplianceLoading(false);
    }
  };

  // Auto Documentation Handler
  const handleGenerateDocs = async () => {
    if (!docsProjectPath.trim()) {
      toast.error('Please enter a project path');
      return;
    }

    setDocsLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/generate-docs`, { project_path: docsProjectPath });
      setDocsResult(response.data);
      toast.success('Documentation generated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Documentation generation failed');
      console.error('Documentation error:', error);
    } finally {
      setDocsLoading(false);
    }
  };

  // Circular Progress Component
  const CircularProgress: React.FC<{ value: number; size?: number }> = ({ value, size = 120 }) => {
    const radius = (size - 10) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value / 100) * circumference;

    return (
      <div className="relative inline-flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-gray-700"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="text-purple-500 transition-all duration-1000 ease-out"
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute text-2xl font-bold text-white">{value}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-white mb-3">Enterprise Dashboard</h2>
        <p className="text-gray-400 text-lg">Advanced tools for enterprise-grade code analysis and optimization</p>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* 1. Git Project Analysis */}
        <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 backdrop-blur-sm rounded-xl p-6 border border-blue-500/30 hover:border-blue-400/50 transition-all shadow-lg hover:shadow-blue-500/20">
          <div className="flex items-center mb-4">
            <span className="text-4xl mr-3">🔍</span>
            <div>
              <h3 className="text-2xl font-bold text-white">Git Project Analysis</h3>
              <p className="text-gray-400 text-sm">Analyze project completeness and quality</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">Git Repository URL</label>
              <input
                type="text"
                value={gitUrl}
                onChange={(e) => setGitUrl(e.target.value)}
                placeholder="https://github.com/user/repo.git"
                className="w-full px-4 py-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>

            <button
              onClick={handleGitAnalysis}
              disabled={gitLoading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {gitLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                'Analyze Project'
              )}
            </button>

            {gitResult && (
              <div className="bg-black/40 rounded-lg p-4 space-y-4 border border-white/10">
                {/* Completion Score */}
                <div className="flex flex-col items-center py-4">
                  <CircularProgress value={gitResult.completion_score} />
                  <p className="text-gray-400 text-sm mt-2">Completion Score</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-red-900/20 rounded-lg p-3 border border-red-500/30">
                    <div className="text-red-400 text-xs mb-1">TODOs</div>
                    <div className="text-2xl font-bold text-white">{gitResult.todo_count}</div>
                  </div>
                  <div className="bg-yellow-900/20 rounded-lg p-3 border border-yellow-500/30">
                    <div className="text-yellow-400 text-xs mb-1">Incomplete</div>
                    <div className="text-2xl font-bold text-white">{gitResult.incomplete_features}</div>
                  </div>
                </div>

                {/* Language Breakdown */}
                <div>
                  <h4 className="text-white font-medium mb-2 text-sm">Language Breakdown</h4>
                  <div className="space-y-2">
                    {gitResult.language_breakdown && Object.entries(gitResult.language_breakdown).map(([lang, percent]) => (
                      <div key={lang}>
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                          <span>{lang}</span>
                          <span>{percent}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full" style={{width: `${percent}%`}}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Git Stats */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="text-center p-2 bg-white/5 rounded">
                    <div className="text-gray-400">Commits</div>
                    <div className="text-white font-bold">{gitResult.git_stats?.total_commits || 0}</div>
                  </div>
                  <div className="text-center p-2 bg-white/5 rounded">
                    <div className="text-gray-400">Contributors</div>
                    <div className="text-white font-bold">{gitResult.git_stats?.contributors || 0}</div>
                  </div>
                  <div className="text-center p-2 bg-white/5 rounded">
                    <div className="text-gray-400">Last Commit</div>
                    <div className="text-white font-bold text-[10px]">{gitResult.git_stats?.last_commit || 'N/A'}</div>
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h4 className="text-white font-medium mb-2 text-sm">Recommendations</h4>
                  <ul className="space-y-1">
                    {gitResult.recommendations?.map((rec, idx) => (
                      <li key={idx} className="text-gray-400 text-xs flex items-start">
                        <span className="text-green-400 mr-2">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 2. Code Refactoring */}
        <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30 hover:border-purple-400/50 transition-all shadow-lg hover:shadow-purple-500/20">
          <div className="flex items-center mb-4">
            <span className="text-4xl mr-3">♻️</span>
            <div>
              <h3 className="text-2xl font-bold text-white">Code Refactoring</h3>
              <p className="text-gray-400 text-sm">Identify and fix code quality issues</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">Project Path</label>
              <input
                type="text"
                value={refactorPath}
                onChange={(e) => setRefactorPath(e.target.value)}
                placeholder="/path/to/your/project"
                className="w-full px-4 py-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition"
              />
            </div>

            <button
              onClick={handleRefactoring}
              disabled={refactorLoading}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {refactorLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                'Analyze Code'
              )}
            </button>

            {refactorResult && (
              <div className="bg-black/40 rounded-lg p-4 space-y-4 border border-white/10">
                {/* Issues Overview */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-red-900/20 rounded-lg p-3 border border-red-500/30 text-center">
                    <div className="text-3xl font-bold text-red-400">{refactorResult.total_issues}</div>
                    <div className="text-gray-400 text-xs mt-1">Total Issues</div>
                  </div>
                  <div className="bg-green-900/20 rounded-lg p-3 border border-green-500/30 text-center">
                    <div className="text-3xl font-bold text-green-400">{refactorResult.potential_loc_savings}</div>
                    <div className="text-gray-400 text-xs mt-1">LOC Savings</div>
                  </div>
                </div>

                {/* Issue Breakdown */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 bg-white/5 rounded">
                    <span className="text-gray-400 text-sm">Dead Code</span>
                    <span className="text-white font-bold">{refactorResult.dead_code_count}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-white/5 rounded">
                    <span className="text-gray-400 text-sm">Duplicates</span>
                    <span className="text-white font-bold">{refactorResult.duplicates_count}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-white/5 rounded">
                    <span className="text-gray-400 text-sm">Complex Functions</span>
                    <span className="text-white font-bold">{refactorResult.high_complexity_functions}</span>
                  </div>
                </div>

                {/* Refactoring Plan */}
                <div>
                  <h4 className="text-white font-medium mb-2 text-sm">Refactoring Plan</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {refactorResult.refactoring_plan?.map((item, idx) => (
                      <div key={idx} className="bg-white/5 rounded p-3 border-l-4 border-purple-500">
                        <div className="flex items-center justify-between mb-1">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                            item.priority === 'HIGH' ? 'bg-red-600 text-white' :
                            item.priority === 'MEDIUM' ? 'bg-yellow-600 text-white' :
                            'bg-green-600 text-white'
                          }`}>
                            {item.priority}
                          </span>
                          <span className="text-gray-500 text-xs">{typeof item.file === 'string' ? item.file : JSON.stringify(item.file)}</span>
                        </div>
                        <div className="text-white text-sm mb-1">{typeof item.issue === 'string' ? item.issue : JSON.stringify(item.issue)}</div>
                        <div className="text-gray-400 text-xs">{typeof item.suggestion === 'string' ? item.suggestion : JSON.stringify(item.suggestion)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 3. Documentation Compliance */}
        <div className="bg-gradient-to-br from-green-900/30 to-teal-900/30 backdrop-blur-sm rounded-xl p-6 border border-green-500/30 hover:border-green-400/50 transition-all shadow-lg hover:shadow-green-500/20">
          <div className="flex items-center mb-4">
            <span className="text-4xl mr-3">📋</span>
            <div>
              <h3 className="text-2xl font-bold text-white">Documentation Compliance</h3>
              <p className="text-gray-400 text-sm">Verify documentation completeness</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">Project Path</label>
              <input
                type="text"
                value={compliancePath}
                onChange={(e) => setCompliancePath(e.target.value)}
                placeholder="/path/to/your/project"
                className="w-full px-4 py-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-green-500 transition"
              />
            </div>

            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">Documentation Path (Optional)</label>
              <input
                type="text"
                value={complianceDocsPath}
                onChange={(e) => setComplianceDocsPath(e.target.value)}
                placeholder="/path/to/docs (optional)"
                className="w-full px-4 py-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-green-500 transition"
              />
            </div>

            <button
              onClick={handleCompliance}
              disabled={complianceLoading}
              className="w-full py-3 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {complianceLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Checking...
                </>
              ) : (
                'Check Compliance'
              )}
            </button>

            {complianceResult && (
              <div className="bg-black/40 rounded-lg p-4 space-y-4 border border-white/10">
                {/* Compliance Score */}
                <div className="flex flex-col items-center py-4">
                  <CircularProgress value={complianceResult.compliance_score} />
                  <p className="text-gray-400 text-sm mt-2">Compliance Score</p>
                </div>

                {/* Compliance Report */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-blue-900/20 rounded-lg p-3 border border-blue-500/30">
                    <div className="text-blue-400 text-xs mb-1">Total Features</div>
                    <div className="text-2xl font-bold text-white">{complianceResult.compliance_report?.total_features}</div>
                  </div>
                  <div className="bg-green-900/20 rounded-lg p-3 border border-green-500/30">
                    <div className="text-green-400 text-xs mb-1">Documented</div>
                    <div className="text-2xl font-bold text-white">{complianceResult.compliance_report?.documented}</div>
                  </div>
                  <div className="bg-purple-900/20 rounded-lg p-3 border border-purple-500/30">
                    <div className="text-purple-400 text-xs mb-1">Implemented</div>
                    <div className="text-2xl font-bold text-white">{complianceResult.compliance_report?.implemented}</div>
                  </div>
                  <div className="bg-red-900/20 rounded-lg p-3 border border-red-500/30">
                    <div className="text-red-400 text-xs mb-1">Missing</div>
                    <div className="text-2xl font-bold text-white">{complianceResult.compliance_report?.missing}</div>
                  </div>
                </div>

                {/* Missing Implementations */}
                {complianceResult.missing_implementations?.length > 0 && (
                  <div>
                    <h4 className="text-white font-medium mb-2 text-sm">Missing Implementations</h4>
                    <div className="space-y-1 max-h-32 overflow-y-auto custom-scrollbar">
                      {complianceResult.missing_implementations?.map((item, idx) => (
                        <div key={idx} className="text-red-400 text-xs flex items-start bg-red-900/10 p-2 rounded">
                          <span className="mr-2">⚠</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Undocumented Features */}
                {complianceResult.undocumented_features?.length > 0 && (
                  <div>
                    <h4 className="text-white font-medium mb-2 text-sm">Undocumented Features</h4>
                    <div className="space-y-1 max-h-32 overflow-y-auto custom-scrollbar">
                      {complianceResult.undocumented_features?.map((item, idx) => (
                        <div key={idx} className="text-yellow-400 text-xs flex items-start bg-yellow-900/10 p-2 rounded">
                          <span className="mr-2">📝</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 4. Auto Documentation Generator */}
        <div className="bg-gradient-to-br from-orange-900/30 to-red-900/30 backdrop-blur-sm rounded-xl p-6 border border-orange-500/30 hover:border-orange-400/50 transition-all shadow-lg hover:shadow-orange-500/20">
          <div className="flex items-center mb-4">
            <span className="text-4xl mr-3">📚</span>
            <div>
              <h3 className="text-2xl font-bold text-white">Auto Documentation</h3>
              <p className="text-gray-400 text-sm">Generate comprehensive documentation</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">Project Path</label>
              <input
                type="text"
                value={docsProjectPath}
                onChange={(e) => setDocsProjectPath(e.target.value)}
                placeholder="/path/to/your/project"
                className="w-full px-4 py-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-orange-500 transition"
              />
            </div>

            <button
              onClick={handleGenerateDocs}
              disabled={docsLoading}
              className="w-full py-3 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white font-medium rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {docsLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </>
              ) : (
                'Generate Docs'
              )}
            </button>

            {docsResult && (
              <div className="bg-black/40 rounded-lg p-4 space-y-4 border border-white/10">
                {/* Generation Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-green-900/20 rounded-lg p-3 border border-green-500/30 text-center">
                    <div className="text-3xl font-bold text-green-400">{docsResult.files_generated}</div>
                    <div className="text-gray-400 text-xs mt-1">Files Generated</div>
                  </div>
                  <div className="bg-blue-900/20 rounded-lg p-3 border border-blue-500/30 text-center">
                    <div className="text-3xl font-bold text-blue-400">{docsResult.documentation_types?.length}</div>
                    <div className="text-gray-400 text-xs mt-1">Doc Types</div>
                  </div>
                </div>

                {/* Documentation Types */}
                <div>
                  <h4 className="text-white font-medium mb-2 text-sm">Documentation Types</h4>
                  <div className="flex flex-wrap gap-2">
                    {docsResult.documentation_types?.map((type, idx) => (
                      <span key={idx} className="px-3 py-1 bg-orange-600/20 text-orange-300 text-xs rounded-full border border-orange-500/30">
                        {type}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Generated Files */}
                <div>
                  <h4 className="text-white font-medium mb-2 text-sm">Generated Files</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {docsResult.generated_files?.map((file, idx) => (
                      <div key={idx} className="bg-white/5 rounded p-3 flex items-center justify-between hover:bg-white/10 transition">
                        <div className="flex-1">
                          <div className="text-white text-sm font-medium">{file.name}</div>
                          <div className="text-gray-400 text-xs mt-1">{file.path}</div>
                          <div className="text-gray-500 text-xs mt-1">Size: {file.size}</div>
                        </div>
                        <a
                          href={file.download_url}
                          download
                          className="ml-3 px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white text-xs rounded transition"
                        >
                          Download
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-xl p-6 border border-purple-500/20">
        <h3 className="text-white font-bold mb-2 flex items-center">
          <span className="mr-2">💡</span>
          Enterprise Features
        </h3>
        <p className="text-gray-400 text-sm mb-3">
          These advanced enterprise tools help you maintain code quality, ensure documentation compliance,
          and automate repetitive tasks. Perfect for teams managing large-scale projects.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="flex items-center text-gray-400">
            <span className="text-green-400 mr-2">✓</span>
            Deep code analysis
          </div>
          <div className="flex items-center text-gray-400">
            <span className="text-green-400 mr-2">✓</span>
            Automated refactoring
          </div>
          <div className="flex items-center text-gray-400">
            <span className="text-green-400 mr-2">✓</span>
            Compliance tracking
          </div>
          <div className="flex items-center text-gray-400">
            <span className="text-green-400 mr-2">✓</span>
            Auto-documentation
          </div>
        </div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(139, 92, 246, 0.7);
        }
      `}</style>
    </div>
  );
};
