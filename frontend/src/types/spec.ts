/**
 * TypeScript interfaces matching backend data models.
 */

export type EntityType = 'Domain' | 'Resource' | 'Actor' | 'Process';

export type RelationshipType =
  | 'one_to_one'
  | 'one_to_many'
  | 'many_to_one'
  | 'many_to_many'
  | 'belongs_to'
  | 'has_many'
  | 'has_one';

export type ConstraintType = 'Performance' | 'Security' | 'Business' | 'Technical' | 'Usability';

export type Priority = 'Must' | 'Should' | 'Could';

export type ConfidenceLevel = 'High' | 'Medium' | 'Low';

export interface Relationship {
  type: RelationshipType;
  target: string;
  description?: string;
}

export interface Entity {
  name: string;
  type: EntityType;
  description: string;
  attributes: string[];
  relationships: Relationship[];
}

export interface Constraint {
  type: ConstraintType;
  description: string;
  priority: Priority;
}

export interface Assumption {
  description: string;
  confidence: ConfidenceLevel;
  needs_clarification: boolean;
}

export interface SpecMetadata {
  generated_at: string;
  processing_time_ms: number;
  confidence_score: number;
  warnings: string[];
}

export interface StructuredSpec {
  goal: string;
  entities: Entity[];
  constraints: Constraint[];
  assumptions: Assumption[];
  metadata: SpecMetadata;
}

export interface IntentRequest {
  text: string;
}

export interface ErrorResponse {
  error: string;
  details: string;
  code: string;
  suggestions?: string[];
}
