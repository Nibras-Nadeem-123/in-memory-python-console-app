/**
 * Goal section component.
 */

interface GoalSectionProps {
  goal: string;
}

export function GoalSection({ goal }: GoalSectionProps) {
  return (
    <section style={styles.section}>
      <h3 style={styles.heading}>🎯 Goal</h3>
      <div style={styles.content}>
        <p style={styles.goalText}>{goal}</p>
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
  goalText: {
    fontSize: '1rem',
    color: '#111827',
    lineHeight: 1.6,
    margin: 0,
  },
};
