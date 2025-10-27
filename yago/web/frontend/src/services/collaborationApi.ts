/**
 * YAGO v7.1 - Collaboration API Service
 * API client for agent collaboration endpoints
 */

import axios from 'axios';
import type {
  AgentMessage,
  Agent,
  SharedContext,
  Conflict,
  TaskDependency,
  SendMessageResponse,
  GetMessagesResponse,
  GetAgentsStatusResponse,
  GetConflictsResponse,
  CollaborationHealth,
  AgentType,
  MessageType,
  MessagePriority,
} from '../types/collaboration';

const API_BASE = 'http://localhost:8000/api/v1/collaboration';

export const collaborationApi = {
  // ========== Messages ==========

  async sendMessage(
    projectId: string,
    fromAgent: AgentType,
    toAgent: AgentType | null,
    messageType: MessageType,
    data: Record<string, any>,
    priority: MessagePriority = MessagePriority.MEDIUM,
    requiresAck: boolean = false
  ): Promise<SendMessageResponse> {
    const { data: response } = await axios.post<SendMessageResponse>(
      `${API_BASE}/messages/send`,
      {
        from_agent: fromAgent,
        to_agent: toAgent,
        message_type: messageType,
        priority,
        data,
        requires_ack: requiresAck,
        project_id: projectId,
      }
    );
    return response;
  },

  async broadcastMessage(
    projectId: string,
    fromAgent: AgentType,
    messageType: MessageType,
    data: Record<string, any>,
    priority: MessagePriority = MessagePriority.MEDIUM
  ): Promise<SendMessageResponse> {
    const { data: response } = await axios.post<SendMessageResponse>(
      `${API_BASE}/messages/broadcast`,
      {
        from_agent: fromAgent,
        message_type: messageType,
        priority,
        data,
        project_id: projectId,
      }
    );
    return response;
  },

  async getMessages(
    projectId: string,
    agent?: AgentType
  ): Promise<GetMessagesResponse> {
    const params = agent ? { agent } : {};
    const { data } = await axios.get<GetMessagesResponse>(
      `${API_BASE}/messages/${projectId}`,
      { params }
    );
    return data;
  },

  async acknowledgeMessage(messageId: string): Promise<{ success: boolean }> {
    const { data } = await axios.post<{ success: boolean }>(
      `${API_BASE}/messages/${messageId}/acknowledge`
    );
    return data;
  },

  // ========== Agents ==========

  async registerAgent(
    projectId: string,
    agentType: AgentType
  ): Promise<Agent> {
    const { data } = await axios.post<Agent>(
      `${API_BASE}/agents/${projectId}/register`,
      null,
      { params: { agent_type: agentType } }
    );
    return data;
  },

  async getAgentsStatus(projectId: string): Promise<GetAgentsStatusResponse> {
    const { data } = await axios.get<GetAgentsStatusResponse>(
      `${API_BASE}/agents/${projectId}/status`
    );
    return data;
  },

  async updateAgentStatus(
    projectId: string,
    agentType: AgentType,
    status: string,
    currentTask?: string
  ): Promise<Agent> {
    const params: any = { status };
    if (currentTask) params.current_task = currentTask;

    const { data } = await axios.put<Agent>(
      `${API_BASE}/agents/${projectId}/${agentType}/status`,
      null,
      { params }
    );
    return data;
  },

  // ========== Shared Context ==========

  async getSharedContext(projectId: string): Promise<SharedContext> {
    const { data } = await axios.get<SharedContext>(
      `${API_BASE}/context/${projectId}`
    );
    return data;
  },

  async updateAgentOutput(
    projectId: string,
    agent: AgentType,
    output: Record<string, any>
  ): Promise<{ success: boolean }> {
    const { data } = await axios.put<{ success: boolean }>(
      `${API_BASE}/context/${projectId}/agent-output`,
      output,
      { params: { agent } }
    );
    return data;
  },

  async addDecision(
    projectId: string,
    decision: Record<string, any>
  ): Promise<{ success: boolean }> {
    const { data } = await axios.post<{ success: boolean }>(
      `${API_BASE}/context/${projectId}/decision`,
      decision
    );
    return data;
  },

  async addIssue(
    projectId: string,
    issue: Record<string, any>
  ): Promise<{ success: boolean }> {
    const { data } = await axios.post<{ success: boolean }>(
      `${API_BASE}/context/${projectId}/issue`,
      issue
    );
    return data;
  },

  async resolveIssue(
    projectId: string,
    issueId: string,
    resolution: string
  ): Promise<{ success: boolean }> {
    const { data } = await axios.post<{ success: boolean }>(
      `${API_BASE}/context/${projectId}/issue/${issueId}/resolve`,
      null,
      { params: { resolution } }
    );
    return data;
  },

  // ========== Conflicts ==========

  async getConflicts(
    projectId: string,
    resolved?: boolean
  ): Promise<GetConflictsResponse> {
    const params = resolved !== undefined ? { resolved } : {};
    const { data } = await axios.get<GetConflictsResponse>(
      `${API_BASE}/conflicts/${projectId}`,
      { params }
    );
    return data;
  },

  async detectConflict(
    projectId: string,
    agentA: AgentType,
    agentB: AgentType,
    description: string,
    proposalA: Record<string, any>,
    proposalB: Record<string, any>
  ): Promise<Conflict> {
    const { data } = await axios.post<Conflict>(
      `${API_BASE}/conflicts/detect`,
      null,
      {
        params: {
          project_id: projectId,
          agent_a: agentA,
          agent_b: agentB,
          description,
          proposal_a: proposalA,
          proposal_b: proposalB,
        },
      }
    );
    return data;
  },

  async resolveConflict(
    conflictId: string,
    resolution: Record<string, any>,
    resolvedBy: string,
    reason: string
  ): Promise<{ success: boolean }> {
    const { data} = await axios.post<{ success: boolean }>(
      `${API_BASE}/conflicts/${conflictId}/resolve`,
      null,
      {
        params: {
          resolution,
          resolved_by: resolvedBy,
          reason,
        },
      }
    );
    return data;
  },

  // ========== Health ==========

  async getHealth(): Promise<CollaborationHealth> {
    const { data } = await axios.get<CollaborationHealth>(
      `${API_BASE}/health`
    );
    return data;
  },

  // ========== WebSocket ==========

  createWebSocket(projectId: string): WebSocket {
    const wsUrl = `ws://localhost:8000/api/v1/collaboration/ws/${projectId}`;
    return new WebSocket(wsUrl);
  },
};
