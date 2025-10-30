/**
 * YAGO v8.3 - Code Preview Component
 * Live preview of generated project files with syntax highlighting
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  size?: number;
  extension?: string;
}

interface FileContent {
  path: string;
  content: string;
  language: string;
  size: number;
  lines: number;
}

interface CodePreviewProps {
  projectId: string;
  projectName: string;
  onClose: () => void;
}

export const CodePreview: React.FC<CodePreviewProps> = ({ projectId, projectName, onClose }) => {
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<FileContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(false);
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadFileTree();
  }, [projectId]);

  const loadFileTree = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/projects/${projectId}/files`
      );
      setFileTree(response.data.files);

      // Auto-expand root directories
      const rootDirs = response.data.files
        .filter((f: FileNode) => f.type === 'directory')
        .map((f: FileNode) => f.path);
      setExpandedDirs(new Set(rootDirs));

      // Auto-select README if exists
      const readme = findFileByName(response.data.files, 'README.md');
      if (readme) {
        loadFileContent(readme.path);
      }
    } catch (error) {
      toast.error('Failed to load project files');
    } finally {
      setLoading(false);
    }
  };

  const findFileByName = (nodes: FileNode[], name: string): FileNode | null => {
    for (const node of nodes) {
      if (node.name === name && node.type === 'file') {
        return node;
      }
      if (node.children) {
        const found = findFileByName(node.children, name);
        if (found) return found;
      }
    }
    return null;
  };

  const loadFileContent = async (filePath: string) => {
    setContentLoading(true);
    setSelectedFile(filePath);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/projects/${projectId}/files/${encodeURIComponent(filePath)}`
      );
      setFileContent(response.data);
    } catch (error) {
      toast.error('Failed to load file content');
      setFileContent(null);
    } finally {
      setContentLoading(false);
    }
  };

  const toggleDirectory = (path: string) => {
    const newExpanded = new Set(expandedDirs);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedDirs(newExpanded);
  };

  const getFileIcon = (node: FileNode): string => {
    if (node.type === 'directory') {
      return expandedDirs.has(node.path) ? '📂' : '📁';
    }

    const ext = node.extension?.toLowerCase() || '';
    const iconMap: { [key: string]: string } = {
      'py': '🐍',
      'js': '📜',
      'ts': '💠',
      'tsx': '⚛️',
      'jsx': '⚛️',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'css': '🎨',
      'html': '🌐',
      'yaml': '⚙️',
      'yml': '⚙️',
      'toml': '⚙️',
      'sh': '🔧',
      'sql': '🗄️',
      'go': '🔵',
      'rs': '🦀',
      'java': '☕',
      'cpp': '⚡',
      'c': '⚡',
    };

    return iconMap[ext] || '📄';
  };

  const getLanguageForFile = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase() || '';
    const langMap: { [key: string]: string } = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'jsx': 'javascript',
      'json': 'json',
      'md': 'markdown',
      'css': 'css',
      'html': 'html',
      'yaml': 'yaml',
      'yml': 'yaml',
      'toml': 'toml',
      'sh': 'bash',
      'sql': 'sql',
      'go': 'go',
      'rs': 'rust',
      'java': 'java',
    };
    return langMap[ext] || 'plaintext';
  };

  const renderFileTree = (nodes: FileNode[], depth = 0) => {
    return nodes.map((node) => (
      <div key={node.path} style={{ paddingLeft: `${depth * 16}px` }}>
        {node.type === 'directory' ? (
          <>
            <button
              onClick={() => toggleDirectory(node.path)}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded flex items-center gap-2 text-sm text-gray-300"
            >
              <span>{getFileIcon(node)}</span>
              <span>{node.name}</span>
              <span className="text-gray-500 text-xs ml-auto">
                {node.children?.length || 0} items
              </span>
            </button>
            {expandedDirs.has(node.path) && node.children && (
              <div>
                {renderFileTree(node.children, depth + 1)}
              </div>
            )}
          </>
        ) : (
          <button
            onClick={() => loadFileContent(node.path)}
            className={`w-full text-left px-3 py-2 hover:bg-white/5 rounded flex items-center gap-2 text-sm ${
              selectedFile === node.path
                ? 'bg-blue-500/20 text-blue-300'
                : 'text-gray-300'
            }`}
          >
            <span>{getFileIcon(node)}</span>
            <span className="flex-1 truncate">{node.name}</span>
            {node.size && (
              <span className="text-gray-500 text-xs">
                {(node.size / 1024).toFixed(1)}KB
              </span>
            )}
          </button>
        )}
      </div>
    ));
  };

  const downloadProject = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/projects/${projectId}/export`,
        { responseType: 'blob' }
      );

      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${projectName || 'project'}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('Project downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download project');
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin text-6xl mb-4">⚙️</div>
          <div className="text-xl">Loading project files...</div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-lg w-full max-w-7xl h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-2xl font-bold text-white">Code Preview</h2>
            <p className="text-gray-400 mt-1">{projectName}</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={downloadProject}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition flex items-center gap-2"
            >
              <span>📦</span>
              <span>Download ZIP</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* File Tree */}
          <div className="w-80 border-r border-white/10 overflow-y-auto bg-black/20">
            <div className="p-4 border-b border-white/10">
              <h3 className="text-sm font-semibold text-gray-400 uppercase">Files</h3>
            </div>
            <div className="py-2">
              {fileTree.length > 0 ? (
                renderFileTree(fileTree)
              ) : (
                <div className="text-gray-500 text-center py-8">No files found</div>
              )}
            </div>
          </div>

          {/* Code Viewer */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {selectedFile && fileContent ? (
              <>
                {/* File Info Bar */}
                <div className="flex items-center justify-between p-4 bg-black/20 border-b border-white/10">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getFileIcon({ name: selectedFile, path: selectedFile, type: 'file', extension: selectedFile.split('.').pop() })}</span>
                    <div>
                      <div className="text-white font-medium">{selectedFile.split('/').pop()}</div>
                      <div className="text-gray-400 text-xs">{selectedFile}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>{fileContent.lines} lines</span>
                    <span>{(fileContent.size / 1024).toFixed(1)}KB</span>
                    <span className="px-2 py-1 bg-white/5 rounded text-xs uppercase">
                      {fileContent.language}
                    </span>
                  </div>
                </div>

                {/* Code Content */}
                <div className="flex-1 overflow-auto bg-black/40">
                  {contentLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-gray-400">Loading file content...</div>
                    </div>
                  ) : (
                    <pre className="p-6 text-sm font-mono text-gray-300 leading-relaxed">
                      <code className={`language-${fileContent.language}`}>
                        {fileContent.content.split('\n').map((line, idx) => (
                          <div key={idx} className="flex">
                            <span className="text-gray-600 select-none w-12 text-right pr-4 flex-shrink-0">
                              {idx + 1}
                            </span>
                            <span className="flex-1">{line || ' '}</span>
                          </div>
                        ))}
                      </code>
                    </pre>
                  )}
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-gray-500">
                  <div className="text-6xl mb-4">📄</div>
                  <div className="text-xl">Select a file to preview</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
