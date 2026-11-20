import axios from 'axios';
import {
  ResearchSession,
  ResearchSessionDetail,
  AgentExecution,
  ResearchSource,
  ResearchReport,
  HealthInfo,
  ResearchMode,
} from '../types';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const api = {
  // Start new research session
  async startResearch(query: string, mode: ResearchMode = 'live'): Promise<ResearchSession> {
    const res = await client.post<ResearchSession>('/research', { query, mode });
    return res.data;
  },

  // Get full session detail with relations
  async getSessionDetail(id: string): Promise<ResearchSessionDetail> {
    const res = await client.get<ResearchSessionDetail>(`/research/${id}`);
    return res.data;
  },

  // Lightweight status polling
  async getSessionStatus(id: string): Promise<{
    id: string;
    query: string;
    mode: string;
    status: string;
    error_message?: string;
    total_sources: number;
    total_claims: number;
    verified_claims: number;
    contradicted_claims: number;
    agents: Array<{
      agent_name: string;
      status: string;
      task_description: string;
      execution_time_ms: number;
      output_summary?: string;
      error_message?: string;
    }>;
    updated_at: string;
  }> {
    const res = await client.get(`/research/${id}/status`);
    return res.data;
  },

  // Get agent logs
  async getSessionAgents(id: string): Promise<AgentExecution[]> {
    const res = await client.get<AgentExecution[]>(`/research/${id}/agents`);
    return res.data;
  },

  // Get sources
  async getSessionSources(id: string): Promise<ResearchSource[]> {
    const res = await client.get<ResearchSource[]>(`/research/${id}/sources`);
    return res.data;
  },

  // Get verified claims
  async getSessionClaims(id: string): Promise<any[]> {
    const res = await client.get(`/research/${id}/claims`);
    return res.data;
  },

  // Get synthesized final report
  async getSessionReport(id: string): Promise<ResearchReport> {
    const res = await client.get<ResearchReport>(`/research/${id}/report`);
    return res.data;
  },

  // Get historical sessions
  async getHistory(skip = 0, limit = 50): Promise<ResearchSession[]> {
    const res = await client.get<ResearchSession[]>('/research/history', {
      params: { skip, limit },
    });
    return res.data;
  },

  // Delete session
  async deleteSession(id: string): Promise<{ message: string; deleted_id: string }> {
    const res = await client.delete(`/research/${id}`);
    return res.data;
  },

  // Check health and available providers
  async getHealth(): Promise<HealthInfo> {
    const res = await client.get<HealthInfo>('/health');
    return res.data;
  },
};
