/**
 * Entities section component.
 */

import type { Entity } from '../types/spec';

interface EntitiesSectionProps {
  entities: Entity[];
}

export function EntitiesSection({ entities }: EntitiesSectionProps) {
  const getTypeColor = (type: string) => {
    const colors = {
      Domain: '#3b82f6',
      Resource: '#10b981',
      Actor: '#f59e0b',
      Process: '#8b5cf6',
    };
    return colors[type as keyof typeof colors] || '#6b7280';
  };

  return (
    <section style={styles.section}>
      <h3 style={styles.heading}>📦 Entities ({entities.length})</h3>
      <div style={styles.content}>
        {entities.map((entity, index) => (
          <div key={index} style={styles.entity}>
            <div style={styles.entityHeader}>
              <h4 style={styles.entityName}>{entity.name}</h4>
              <span
                style={{
                  ...styles.typeBadge,
                  backgroundColor: `${getTypeColor(entity.type)}20`,
                  color: getTypeColor(entity.type),
                }}
              >
                {entity.type}
              </span>
            </div>
            <p style={styles.description}>{entity.description}</p>

            <div style={styles.attributes}>
              <strong style={styles.attributesLabel}>Attributes:</strong>
              <div style={styles.attributesList}>
                {entity.attributes.map((attr, i) => (
                  <span key={i} style={styles.attributeTag}>
                    {attr}
                  </span>
                ))}
              </div>
            </div>

            {entity.relationships.length > 0 && (
              <div style={styles.relationships}>
                <strong style={styles.relationshipsLabel}>Relationships:</strong>
                <ul style={styles.relationshipsList}>
                  {entity.relationships.map((rel, i) => (
                    <li key={i} style={styles.relationshipItem}>
                      <code style={styles.relationshipType}>{rel.type}</code>
                      <span style={styles.relationshipTarget}>{rel.target}</span>
                      {rel.description && (
                        <span style={styles.relationshipDesc}>- {rel.description}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
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
  entity: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '0.375rem',
    padding: '1rem',
  },
  entityHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
  entityName: {
    fontSize: '1rem',
    fontWeight: 600,
    color: '#111827',
    margin: 0,
  },
  typeBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
  },
  description: {
    color: '#6b7280',
    fontSize: '0.875rem',
    marginBottom: '0.75rem',
  },
  attributes: {
    marginBottom: '0.75rem',
  },
  attributesLabel: {
    fontSize: '0.875rem',
    color: '#374151',
    display: 'block',
    marginBottom: '0.5rem',
  },
  attributesList: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '0.5rem',
  },
  attributeTag: {
    backgroundColor: '#f3f4f6',
    color: '#374151',
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontFamily: 'monospace',
  },
  relationships: {
    marginTop: '0.75rem',
  },
  relationshipsLabel: {
    fontSize: '0.875rem',
    color: '#374151',
    display: 'block',
    marginBottom: '0.5rem',
  },
  relationshipsList: {
    margin: 0,
    paddingLeft: '1.25rem',
    fontSize: '0.875rem',
  },
  relationshipItem: {
    marginBottom: '0.25rem',
    color: '#6b7280',
  },
  relationshipType: {
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    padding: '0.125rem 0.375rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontFamily: 'monospace',
    marginRight: '0.5rem',
  },
  relationshipTarget: {
    fontWeight: 600,
    color: '#374151',
    marginRight: '0.5rem',
  },
  relationshipDesc: {
    color: '#6b7280',
  },
};
