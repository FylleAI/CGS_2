/**
 * Pack Types for Fylle Onboarding v3
 * Packs are content generation templates (Newsletter, Blog Post, etc.)
 */

export interface Pack {
  id: string;
  name: string;
  displayName: string;
  description: string;
  icon?: string;
  isActive: boolean;
  createdAt: string;
}

export interface BriefQuestion {
  id: string;
  question: string;
  options: string[];
  required: boolean;
  section: BriefSection;
  reason?: string;
}

export enum BriefSection {
  BRAND_VOICE = 'brand_voice',
  EDITORIAL_STRUCTURE = 'editorial_structure',
  CITATIONS = 'citations',
  NON_NEGOTIABLES = 'non_negotiables',
}

export interface BriefDocument {
  id?: string;
  userId: string;
  packId: string;
  title?: string;
  purpose: string;
  nonNegotiables: Record<string, string>;
  brandVoice: {
    voice: string;
    styleRules: string[];
    emojiPolicy: string;
    opening: string;
    bannedPhrasing: string[];
  };
  glossary: Record<string, string>;
  editorialStructure: {
    format: string;
    sections: string[];
    sectionDetails: Record<string, string>;
  };
  citationRules: {
    format: string;
    placement: string;
    sources: string[];
    dateRules: string;
  };
  createdAt: string;
}

export interface StartBriefRequest {
  packId: string;
}

export interface StartBriefResponse {
  briefSessionId: string;
  questions: BriefQuestion[];
  message: string;
}

export interface SubmitBriefAnswersRequest {
  answers: Record<string, string>;
}

export interface SubmitBriefAnswersResponse {
  briefId: string;
  brief: BriefDocument;
  message: string;
}

// Default packs
export const DEFAULT_PACKS: Pack[] = [
  {
    id: 'newsletter',
    name: 'newsletter',
    displayName: 'Newsletter Pack',
    description: 'Genera brief per newsletter professionali',
    icon: '📧',
    isActive: true,
    createdAt: new Date().toISOString(),
  },
  {
    id: 'blog_post',
    name: 'blog_post',
    displayName: 'Blog Post Pack',
    description: 'Genera brief per articoli di blog',
    icon: '📝',
    isActive: true,
    createdAt: new Date().toISOString(),
  },
];
