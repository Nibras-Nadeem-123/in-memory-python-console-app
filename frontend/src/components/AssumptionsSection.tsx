/**
 * Assumptions section component.
 */

import type { Assumption } from '../types/spec';

interface AssumptionsSectionProps {
  assumptions: Assumption[];
}

export function AssumptionsSection({ assumptions }: AssumptionsSectionProps) {
  const getConfidenceColor = (confidence: string) => {
    const colors = {
      High: '#10b981',
      Medium: '#f59e0b',
      Low: '#ef4444',
    };
    return colors[confidence as keyof typeof colors] || '#6b7280';
  };

  return (
    <section style={styles.section}>
      <h3 style={styles.heading}>💭 Assumptions ({assumptions.length})</h3>
      <div style={styles.content}>
        {assumptions.length === 0 ? (
          <p style={styles.emptyText}>No assumptions detected</p>
        ) : (
          <ul style={styles.assumptionsList}>
            {assumptions.map((assumption, index) => (
              <li key={index} style={styles.assumptionItem}>
                <div style={styles.assumptionHeader}>
                  <span
                    style={{
                      ...styles.confidenceBadge,
                      backgroundColor: `${getConfidenceColor(assumption.confidence)}20`,
                      color: getConfidenceColor(assumption.confidence),
                    }}
                  >
                    {assumption.confidence} Confidence
                  </span>
                  {assumption.needs_clarification && (
                    <span style={styles.clarificationBadge}>⚠️ Needs Clarification</span>
                  )}
                </div>
                <p style={styles.assumptionText}>{assumption.description}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

const styles = {
  section: {
    backgroundColor: '#fef3c7',
    border: '1px solid #fcd34d',
    borderRadius: '0.375rem',
    padding: '1rem',
  },
  heading: {
    fontSize: '1.125rem',
    fontWeight: 600,
    color: '#92400e',
    marginBottom: '0.75rem',
    margin: 0,
  },
  content: {
    paddingLeft: '1.5rem',
  },
  emptyText: {
    color: '#92400e',
    fontSize: '0.875rem',
    fontStyle: 'italic',
  },
  assumptionsList: {
    margin: 0,
    paddingLeft: 0,
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.75rem',
  },
  assumptionItem: {
    backgroundColor: '#ffffff',
    border: '1px solid #fcd34d',
    borderRadius: '0.375rem',
    padding: '0.75rem',
  },
  assumptionHeader: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '0.5rem',
    flexWrap: 'wrap' as const,
  },
  confidenceBadge: {
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
  },
  clarificationBadge: {
    backgroundColor: '#fed7aa',
    color: '#9a3412',
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
  },
  assumptionText: {
    fontSize: '0.875rem',
    color: '#78350f',
    margin: 0,
    lineHeight: 1.5,
  },
};
