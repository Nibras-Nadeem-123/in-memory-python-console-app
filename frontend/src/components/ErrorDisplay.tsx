/**
 * Error display component with retry capability.
 */

import { APIError } from '../api/client';

interface ErrorDisplayProps {
  error: APIError;
  onRetry?: () => void;
}

export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>⚠️ Error</h3>
        <span style={styles.code}>{error.code}</span>
      </div>

      <p style={styles.message}>{error.message}</p>

      {error.details && <p style={styles.details}>{error.details}</p>}

      {error.suggestions && error.suggestions.length > 0 && (
        <div style={styles.suggestions}>
          <h4 style={styles.suggestionsTitle}>Suggestions:</h4>
          <ul style={styles.suggestionsList}>
            {error.suggestions.map((suggestion, index) => (
              <li key={index} style={styles.suggestionItem}>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {onRetry && (
        <button onClick={onRetry} style={styles.retryButton}>
          Try Again
        </button>
      )}
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#fee2e2',
    border: '1px solid #fecaca',
    borderRadius: '0.5rem',
    padding: '1.5rem',
    marginBottom: '2rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  title: {
    color: '#dc2626',
    fontSize: '1.125rem',
    fontWeight: 600,
    margin: 0,
  },
  code: {
    backgroundColor: '#fecaca',
    color: '#991b1b',
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
    fontFamily: 'monospace',
  },
  message: {
    color: '#991b1b',
    fontWeight: 600,
    marginBottom: '0.5rem',
  },
  details: {
    color: '#7f1d1d',
    fontSize: '0.875rem',
    marginBottom: '1rem',
  },
  suggestions: {
    backgroundColor: '#ffffff',
    border: '1px solid #fecaca',
    borderRadius: '0.375rem',
    padding: '1rem',
    marginBottom: '1rem',
  },
  suggestionsTitle: {
    color: '#991b1b',
    fontSize: '0.875rem',
    fontWeight: 600,
    marginBottom: '0.5rem',
  },
  suggestionsList: {
    margin: 0,
    paddingLeft: '1.25rem',
    color: '#7f1d1d',
    fontSize: '0.875rem',
  },
  suggestionItem: {
    marginBottom: '0.25rem',
  },
  retryButton: {
    backgroundColor: '#dc2626',
    color: '#ffffff',
    padding: '0.5rem 1rem',
    borderRadius: '0.375rem',
    fontWeight: 600,
    fontSize: '0.875rem',
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
};
