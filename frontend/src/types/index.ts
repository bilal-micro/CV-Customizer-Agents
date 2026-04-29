export interface StageResult {
  id: string;
  stage: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: Record<string, unknown>;
  rating: number | null;
  notes: string;
  iteration_notes: string;
  manual_feedback: string;
  iteration_number: number;
  created_at: string;
  updated_at: string;
}

export interface ProcessRun {
  id: string;
  job: string;
  status: 'pending' | 'running' | 'awaiting_manual_input' | 'completed' | 'failed';
  retry_count: number;
  max_retries: number;
  iteration_count: number;
  max_iterations: number;
  manual_latex_input: string;
  stage_results: StageResult[];
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  title: string;
  description: string;
  latex_cv: string;
  process_runs: ProcessRun[];
  created_at: string;
}

export interface JobCreate {
  title: string;
  description: string;
  latex_cv: string;
}

export interface ExtractedKeyword {
  skill?: string;  // For hard_skills, soft_skills
  keyword?: string;  // For keywords
  item?: string;   // For must_have, nice_to_have
  qualification?: string;  // For qualifications
  priority: number;  // 1-10 scale
  category: string;  // e.g., programming_language, interpersonal, education
  placement_hints: string[];  // Suggested CV sections
  confidence: number;  // 0.0-1.0
}

export interface MatchedKeyword {
  keyword: string;
  location: string;
  context: string;
  effectiveness_score: number;
  usage_quality: string;
  similarity_score?: number;
}

export interface MissingKeyword {
  keyword: string;
  reason: string;
  priority_impact: string;
  suggested_location: string;
}

export type KeywordItem = string | ExtractedKeyword | MatchedKeyword | MissingKeyword;
