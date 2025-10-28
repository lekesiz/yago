/**
 * YAGO v7.1 - Agent Collaboration Types
 * TypeScript definitions for agent collaboration and message passing
 */

export enum MessageType {
  CODE_READY = 'code_ready',
  TEST_RESULTS = 'test_results',
  REVIEW_NEEDED = 'review_needed',
  ISSUE_FOUND = 'issue_found',
  FIX_REQUESTED = 'fix_requested',
  DOCUMENTATION_READY = 'documentation_ready',
  CLARIFICATION_NEEDED = 'clarification_needed',
  TASK_COMPLETED = 'task_completed',
  TASK_FAILED = 'task_failed',
  CONFLICT_DETECTED = 'conflict_detected',
}

export enum MessagePriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export enum AgentType {
  PLANNER = 'Planner',
  CODER = 'Coder',
  TESTER = 'Tester',
  REVIEWER = 'Reviewer',
  DOCUMENTER = 'Documenter',
  SECURITY = 'SecurityAgent',
  DEVOPS = 'DevOpsAgent',
  DATABASE = 'DatabaseAgent',
  FRONTEND = 'FrontendAgent',
  BACKEND = 'BackendAgent',
}

export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  WAITING = 'waiting',
  ERROR = 'error',
}

export interface AgentMessage {
  id: string;
  from_agent: AgentType;
  to_agent: AgentType | null; // null = broadcast
  message_type: MessageType;
  priority: MessagePriority;
  content: string;
  data: Record<string, any>;
  requires_ack: boolean;
  timeout: number; // seconds
  timestamp: string;
  project_id: string;
  session_id?: string | null;
  acknowledged: boolean;
  ack_timestamp?: string | null;
  response_to?: string | null;
  metadata?: Record<string, any>;
}

export interface Agent {
  agent_id: string;
  agent_type: AgentType;
  status: AgentStatus;
  current_task: string | null;
  last_activity: string;
  messages_sent: number;
  messages_received: number;
  tasks_completed: number;
  tasks_failed: number;
}

export interface SharedContext {
  project_id: string;
  timestamp: string;
  tech_stack: Record<string, any>;
  architecture: Record<string, any>;
  security_requirements: string[];
  test_requirements: Record<string, any>;
  deployment_target: Record<string, any>;
  agent_outputs: Record<string, Record<string, any>>;
  active_issues: Issue[];
  decisions: Decision[];
}

export interface Issue {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  created_by: AgentType;
  created_at: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  assigned_to?: AgentType;
  resolution?: string;
  resolved_at?: string;
}

export interface Decision {
  id: string;
  description: string;
  made_by: AgentType;
  timestamp: string;
  rationale: string;
  alternatives?: string[];
  impact: 'low' | 'medium' | 'high';
}

export interface Conflict {
  id: string;
  project_id: string;
  agent_a: AgentType;
  agent_b: AgentType;
  description: string;
  agent_a_proposal: Record<string, any>;
  agent_b_proposal: Record<string, any>;
  resolution: Record<string, any> | null;
  resolved: boolean;
  resolved_by: string | null;
  resolution_reason: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface TaskDependency {
  task_id: string;
  agent: AgentType;
  depends_on: string[];
  status: 'pending' | 'ready' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
}

// API Response types
export interface SendMessageResponse {
  success: boolean;
  message_id: string;
  timestamp: string;
  broadcast?: boolean;
}

export interface GetMessagesResponse {
  project_id: string;
  agent: string;
  total: number;
  messages: AgentMessage[];
}

export interface GetAgentsStatusResponse {
  project_id: string;
  total_agents: number;
  agents: Agent[];
}

export interface GetConflictsResponse {
  project_id: string;
  total: number;
  conflicts: Conflict[];
}

export interface CollaborationHealth {
  status: 'healthy' | 'unhealthy';
  total_projects: number;
  total_messages: number;
  active_agents: number;
  active_conflicts: number;
  websocket_connections: number;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'agent_message' | 'context_update' | 'agent_status' | 'conflict' | 'pong';
  data?: any;
  message?: AgentMessage;
  agent?: string;
  timestamp?: string;
}

// Chart data for visualizations
export interface AgentActivityData {
  agent: AgentType;
  messages_sent: number;
  messages_received: number;
  tasks_completed: number;
  tasks_failed: number;
  efficiency: number; // tasks_completed / (tasks_completed + tasks_failed)
}

export interface MessageFlowData {
  from: AgentType;
  to: AgentType;
  count: number;
  types: {
    [key in MessageType]?: number;
  };
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  agent: AgentType;
  event_type: 'message' | 'task' | 'issue' | 'decision' | 'conflict';
  description: string;
  data: any;
}
