/**
 * Metadata section component.
 */

import type { SpecMetadata } from '../types/spec';

interface MetadataSectionProps {
  metadata: SpecMetadata;
}

export function MetadataSection({ metadata }: MetadataSectionProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return { label: 'High', color: '#10b981' };
    if (score >= 0.6) return { label: 'Medium', color: '#f59e0b' };
    return { label: 'Low', color: '#ef4444' };
  };

  const confidenceInfo = getConfidenceLabel(metadata.confidence_score);

  return (
    <section style={styles.section}>
      <h3 style={styles.heading}>📊 Metadata</h3>
      <div style={styles.content}>
        <div style={styles.grid}>
          <div style={styles.metadataItem}>
            <span style={styles.label}>Generated At:</span>
            <span style={styles.value}>{formatDate(metadata.generated_at)}</span>
          </div>

          <div style={styles.metadataItem}>
            <span style={styles.label}>Processing Time:</span>
            <span style={styles.value}>{metadata.processing_time_ms.toFixed(2)} ms</span>
          </div>

          <div style={styles.metadataItem}>
            <span style={styles.label}>Confidence Score:</span>
            <div style={styles.confidenceContainer}>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${metadata.confidence_score * 100}%`,
                    backgroundColor: confidenceInfo.color,
                  }}
                />
              </div>
              <span
                style={{
                  ...styles.confidenceBadge,
                  color: confidenceInfo.color,
                }}
              >
                {(metadata.confidence_score * 100).toFixed(0)}% ({confidenceInfo.label})
              </span>
            </div>
          </div>
        </div>

        {metadata.warnings.length > 0 && (
          <div style={styles.warnings}>
            <h4 style={styles.warningsHeading}>⚠️ Warnings:</h4>
            <ul style={styles.warningsList}>
              {metadata.warnings.map((warning, index) => (
                <li key={index} style={styles.warningItem}>
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}

const styles = {
  section: {
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '0.375rem',
    padding: '1rem',
  },
  heading: {
    fontSize: '1.125rem',
    fontWeight: 600,
    color: '#374151',
    marginBottom: '0.75rem',
    margin: 0,
  },
  content: {
    paddingLeft: '1.5rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '1rem',
  },
  metadataItem: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.25rem',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#6b7280',
  },
  value: {
    fontSize: '0.875rem',
    color: '#111827',
  },
  confidenceContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  progressBar: {
    width: '100%',
    height: '0.5rem',
    backgroundColor: '#e5e7eb',
    borderRadius: '0.25rem',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    transition: 'width 0.3s ease',
  },
  confidenceBadge: {
    fontSize: '0.875rem',
    fontWeight: 600,
  },
  warnings: {
    marginTop: '1rem',
    backgroundColor: '#fef3c7',
    border: '1px solid #fcd34d',
    borderRadius: '0.375rem',
    padding: '0.75rem',
  },
  warningsHeading: {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: '#92400e',
    marginBottom: '0.5rem',
    margin: 0,
  },
  warningsList: {
    margin: 0,
    paddingLeft: '1.25rem',
    color: '#78350f',
    fontSize: '0.875rem',
  },
  warningItem: {
    marginBottom: '0.25rem',
  },
};
