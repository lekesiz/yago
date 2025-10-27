/**
 * YAGO v7.1 - Template Types
 * TypeScript types for project templates
 */

export interface TemplateInfo {
  id: string;
  name: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  icon: string;
  tags: string[];
  estimated_duration: string;
  estimated_cost: number;
  file: string;
  popular: boolean;
  description?: string;
}

export interface TemplateCategory {
  id: string;
  name: string;
  description: string;
  count: number;
}

export interface DifficultyLevel {
  [key: string]: string;
}

export interface TemplatesResponse {
  total: number;
  templates: TemplateInfo[];
  categories: TemplateCategory[];
  difficulty_levels: DifficultyLevel[];
}

export interface TemplateDetail {
  id: string;
  name: string;
  version: string;
  category: string;
  description: string;
  icon: string;
  tags: string[];
  difficulty: string;
  estimated_duration: string;
  estimated_tokens: number;
  estimated_cost: number;
  tech_stack: Record<string, any>;
  agents: Array<{
    name: string;
    priority: number;
    tasks?: string[];
  }>;
  features: Record<string, any>;
  deployment?: Record<string, any>;
  success_criteria?: string[];
  metadata: {
    author: string;
    created_at: string;
    version: string;
    status: string;
  };
}

export interface TemplatePreview {
  id: string;
  name: string;
  description: string;
  icon: string;
  difficulty: string;
  estimated_duration: string;
  estimated_cost: number;
  tech_stack: Record<string, any>;
  features: string[] | Record<string, any>;
  tags: string[];
}
