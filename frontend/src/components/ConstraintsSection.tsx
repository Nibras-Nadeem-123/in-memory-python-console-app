/**
 * Constraints section component.
 */

import type { Constraint } from '../types/spec';

interface ConstraintsSectionProps {
  constraints: Constraint[];
}

export function ConstraintsSection({ constraints }: ConstraintsSectionProps) {
  const getPriorityColor = (priority: string) => {
    const colors = {
      Must: '#dc2626',
      Should: '#f59e0b',
      Could: '#3b82f6',
    };
    return colors[priority as keyof typeof colors] || '#6b7280';
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      Performance: '⚡',
      Security: '🔒',
      Business: '💼',
      Technical: '⚙️',
      Usability: '👥',
    };
    return icons[type as keyof typeof icons] || '📋';
  };

  // Group by priority
  const grouped = constraints.reduce((acc, constraint) => {
    const priority = constraint.priority;
    if (!acc[priority]) acc[priority] = [];
    acc[priority].push(constraint);
    return acc;
  }, {} as Record<string, Constraint[]>);

  const priorityOrder = ['Must', 'Should', 'Could'];

  return (
    <section style={styles.section}>
      <h3 style={styles.heading}>📋 Constraints ({constraints.length})</h3>
      <div style={styles.content}>
        {priorityOrder.map(
          (priority) =>
            grouped[priority] && (
              <div key={priority} style={styles.priorityGroup}>
                <h4
                  style={{
                    ...styles.priorityHeading,
                    color: getPriorityColor(priority),
                  }}
                >
                  {priority} Have ({grouped[priority].length})
                </h4>
                <ul style={styles.constraintsList}>
                  {grouped[priority].map((constraint, index) => (
                    <li key={index} style={styles.constraintItem}>
                      <div style={styles.constraintHeader}>
                        <span style={styles.typeIcon}>{getTypeIcon(constraint.type)}</span>
                        <span
                          style={{
                            ...styles.typeBadge,
                            borderColor: getPriorityColor(priority),
                          }}
                        >
                          {constraint.type}
                        </span>
                      </div>
                      <p style={styles.constraintText}>{constraint.description}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )
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
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
  },
  priorityGroup: {
    marginBottom: '0.5rem',
  },
  priorityHeading: {
    fontSize: '1rem',
    fontWeight: 600,
    marginBottom: '0.5rem',
  },
  constraintsList: {
    margin: 0,
    paddingLeft: 0,
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.75rem',
  },
  constraintItem: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '0.375rem',
    padding: '0.75rem',
  },
  constraintHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginBottom: '0.5rem',
  },
  typeIcon: {
    fontSize: '1.25rem',
  },
  typeBadge: {
    border: '1px solid',
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
  },
  constraintText: {
    fontSize: '0.875rem',
    color: '#374151',
    margin: 0,
    lineHeight: 1.5,
  },
};
