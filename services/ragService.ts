/**
 * RAG API Service
 * Connects React frontend to Python RAG backend
 */

const RAG_API_URL = 'http://localhost:8000';

export interface Disease {
  id: string;
  name: string;
  source: string;
  category: string;
  sections: string[];
}

export interface CategoryCount {
  name: string;
  count: number;
}

export interface QueryResult {
  answer: string;
  sources: {
    content: string;
    chunk_title: string;
    section_title: string;
    source_file: string;
  }[];
}

export interface GeneratedCase {
  case: string;
  symptoms: string;
  disease: string;
}

export interface EvaluationResult {
  case: string;
  standard: string;
  evaluation: string;
  sources: {
    content: string;
    chunk_title: string;
    section_title: string;
    source_file: string;
  }[];
}

class RagService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = RAG_API_URL;
  }

  /**
   * Check if RAG API is available
   */
  async checkHealth(): Promise<{
    status: string;
    rag_ready: boolean;
    evaluator_ready: boolean;
    diseases_loaded: number;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) throw new Error('API not available');
      return await response.json();
    } catch (error) {
      console.error('RAG API health check failed:', error);
      throw error;
    }
  }

  /**
   * Get all diseases from RAG database
   */
  async getDiseases(category?: string, search?: string): Promise<Disease[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    
    const url = `${this.baseUrl}/diseases${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch diseases');
    }
    
    return await response.json();
  }

  /**
   * Get disease categories
   */
  async getCategories(): Promise<CategoryCount[]> {
    const response = await fetch(`${this.baseUrl}/categories`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }
    
    return await response.json();
  }

  /**
   * Query the RAG knowledge base
   */
  async queryKnowledge(question: string): Promise<QueryResult> {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, k: 3 }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to query knowledge base');
    }
    
    return await response.json();
  }

  /**
   * Generate a patient case for training
   */
  async generateCase(disease: string): Promise<GeneratedCase> {
    const response = await fetch(`${this.baseUrl}/generate-case`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disease }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate case');
    }
    
    return await response.json();
  }

  /**
   * Evaluate doctor's answer against RAG knowledge
   */
  async evaluateAnswer(
    disease: string,
    caseText: string,
    doctorAnswer: string
  ): Promise<EvaluationResult> {
    const response = await fetch(`${this.baseUrl}/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disease,
        case: caseText,
        doctor_answer: doctorAnswer,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to evaluate answer');
    }
    
    return await response.json();
  }

  /**
   * Get a specific disease by ID
   */
  async getDisease(diseaseId: string): Promise<Disease> {
    const response = await fetch(`${this.baseUrl}/diseases/${diseaseId}`);
    
    if (!response.ok) {
      throw new Error('Disease not found');
    }
    
    return await response.json();
  }
}

// Export singleton instance
export const ragService = new RagService();
