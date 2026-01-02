/**
 * Spec output container component.
 */

import type { StructuredSpec } from '../types/spec';
import { GoalSection } from './GoalSection';
import { EntitiesSection } from './EntitiesSection';
import { ConstraintsSection } from './ConstraintsSection';
import { AssumptionsSection } from './AssumptionsSection';
import { MetadataSection } from './MetadataSection';

interface SpecOutputProps {
  spec: StructuredSpec;
}

export function SpecOutput({ spec }: SpecOutputProps) {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Generated Specification</h2>
        <span style={styles.badge}>
          Confidence: {(spec.metadata.confidence_score * 100).toFixed(0)}%
        </span>
      </div>

      <div style={styles.sections}>
        <GoalSection goal={spec.goal} />
        <EntitiesSection entities={spec.entities} />
        <ConstraintsSection constraints={spec.constraints} />
        {spec.assumptions.length > 0 && <AssumptionsSection assumptions={spec.assumptions} />}
        <MetadataSection metadata={spec.metadata} />
      </div>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '0.5rem',
    padding: '1.5rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
    paddingBottom: '1rem',
    borderBottom: '2px solid #e5e7eb',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#111827',
    margin: 0,
  },
  badge: {
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    padding: '0.5rem 1rem',
    borderRadius: '0.375rem',
    fontSize: '0.875rem',
    fontWeight: 600,
  },
  sections: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1.5rem',
  },
};
