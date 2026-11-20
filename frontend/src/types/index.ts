export type VerificationStatus = 
  | 'SUPPORTED' 
  | 'CONTRADICTED' 
  | 'PARTIALLY_SUPPORTED' 
  | 'INSUFFICIENT_EVIDENCE' 
  | 'CONFLICTING_EVIDENCE';

export type AgentStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';

export type ResearchMode = 'live' | 'demo';

export interface AgentExecution {
  id: string;
  session_id: string;
  agent_name: string;
  status: AgentStatus;
  task_description: string;
  execution_time_ms: number;
  output_summary?: string;
  output_data?: Record<string, any>;
  error_message?: string;
  created_at: string;
}

export interface ResearchSource {
  id: string;
  session_id: string;
  source_id: string;
  title: string;
  url: string;
  domain: string;
  publication_date?: string;
  snippet: string;
  source_type: 'government' | 'academic' | 'industry' | 'news' | 'web';
  reliability_score: number;
  reliability_rationale?: string;
  created_at: string;
}

export interface ExtractedClaim {
  id: string;
  session_id: string;
  claim_id: string;
  claim_text: string;
  evidence_type: string;
  confidence: number;
  source_ids: string[];
  created_at: string;
}

export interface ClaimVerification {
  id: string;
  session_id: string;
  claim_id: string;
  verification_status: VerificationStatus;
  explanation: string;
  supporting_sources: string[];
  contradicting_sources: string[];
  limitations?: string;
  created_at: string;
}

export interface ContradictionItem {
  claim_ids: string[];
  conflicting_sources: string[];
  statement_a: string;
  statement_b: string;
  divergence_reason: string;
  analysis: string;
}

export interface ResearchReport {
  id: string;
  session_id: string;
  report_title: string;
  executive_summary: string;
  methodology: string;
  key_findings: string[];
  limitations: string;
  conclusion: string;
  markdown_content: string;
  references: Array<{
    source_id: string;
    title: string;
    url: string;
    domain: string;
    publication_date?: string;
    reliability_score?: number;
  }>;
  contradiction_analysis?: ContradictionItem[];
  created_at: string;
}

export interface ResearchSession {
  id: string;
  query: string;
  mode: ResearchMode;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  error_message?: string;
  total_sources: number;
  total_claims: number;
  verified_claims: number;
  contradicted_claims: number;
  partially_supported_claims: number;
  insufficient_claims: number;
  conflicting_claims: number;
  created_at: string;
  updated_at: string;
}

export interface ResearchSessionDetail extends ResearchSession {
  agent_executions: AgentExecution[];
  sources: ResearchSource[];
  claims: ExtractedClaim[];
  verifications: ClaimVerification[];
  report?: ResearchReport;
}

export interface HealthInfo {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  providers: {
    llm: {
      configured: boolean;
      provider: string;
      model: string;
    };
    search: {
      configured: boolean;
      provider: string;
    };
  };
  live_mode_available: boolean;
  demo_mode_available: boolean;
}
