export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  timestamp: number;
  isError?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  updatedAt: number;
}

export interface UserSettings {
  theme: 'light' | 'dark'; // Placeholder for future
}

// ============ Training Session Types ============

export type CaseType = 'random' | 'customised';
export type SessionStatus = 'in-progress' | 'pending-evaluation' | 'completed';
export type ClinicalSystem = 'respiratory' | 'cardiovascular' | 'gastrointestinal' | 'neurological' | 'infectious' | 'endocrine' | 'renal' | 'hematological';
export type DifficultyLevel = 'easy' | 'medium' | 'hard';
export type AgeGroup = 'neonatal' | 'infant' | 'toddler' | 'preschool' | 'school-age' | 'adolescent';

export interface CaseConfig {
  caseType: CaseType;
  ageGroup?: AgeGroup;
  ageRange?: { min: number; max: number };
  clinicalSystem?: ClinicalSystem;
  difficulty?: DifficultyLevel;
  practiceMode?: boolean;
}

export interface PatientInfo {
  caseId: string;
  name: string;
  age: number;
  ageUnit: 'days' | 'months' | 'years';
  gender: 'male' | 'female';
  chiefComplaint: string;
  clinicalSystem: ClinicalSystem;
  difficulty: DifficultyLevel;
  caseType: CaseType;
}

export interface DiagnosisSubmission {
  provisionalDiagnosis: string;
  differentialDiagnoses: string[];
  managementPlan: string;
  submittedAt: number;
}

export interface EvaluationResult {
  overallScore: number;
  maxScore: number;
  subScores: {
    historyTaking: number;
    physicalExamination: number;
    diagnosis: number;
    managementPlan: number;
  };
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  detailedFeedback: string;
  evaluatedAt: number;
}

export interface TrainingSession {
  id: string;
  caseConfig: CaseConfig;
  patientInfo: PatientInfo | null;
  messages: Message[];
  diagnosis: DiagnosisSubmission | null;
  evaluation: EvaluationResult | null;
  status: SessionStatus;
  interactionCount: number;
  createdAt: number;
  updatedAt: number;
}

export type AppView = 'home' | 'case-selection' | 'consultation' | 'diagnosis' | 'feedback' | 'history';
