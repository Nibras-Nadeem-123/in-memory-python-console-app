/**
 * Intent input component with word count validation.
 */

import { useState, ChangeEvent, FormEvent } from 'react';

interface IntentInputProps {
  onSubmit: (intent: string) => void;
  isLoading?: boolean;
}

export function IntentInput({ onSubmit, isLoading = false }: IntentInputProps) {
  const [intent, setIntent] = useState('');
  const [error, setError] = useState('');

  // Calculate word count
  const wordCount = intent.trim() ? intent.trim().split(/\s+/).length : 0;
  const isValid = wordCount >= 50 && wordCount <= 500;

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setIntent(e.target.value);
    setError('');
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!intent.trim()) {
      setError('Please enter your intent');
      return;
    }

    if (wordCount < 50) {
      setError(`Intent must be at least 50 words. Current: ${wordCount} words.`);
      return;
    }

    if (wordCount > 500) {
      setError(`Intent must be at most 500 words. Current: ${wordCount} words.`);
      return;
    }

    onSubmit(intent);
  };

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label htmlFor="intent" style={styles.label}>
            Describe your system intent
          </label>
          <textarea
            id="intent"
            value={intent}
            onChange={handleChange}
            placeholder="Describe what you want to build (50-500 words)..."
            disabled={isLoading}
            style={{
              ...styles.textarea,
              borderColor: error ? '#ef4444' : '#d1d5db',
            }}
            rows={10}
          />

          <div style={styles.footer}>
            <div style={styles.wordCount}>
              <span
                style={{
                  color:
                    wordCount < 50
                      ? '#ef4444'
                      : wordCount > 500
                      ? '#ef4444'
                      : wordCount >= 50
                      ? '#10b981'
                      : '#6b7280',
                }}
              >
                {wordCount}
              </span>
              <span style={{ color: '#6b7280' }}> / 50-500 words</span>
            </div>

            {error && <div style={styles.error}>{error}</div>}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !isValid}
          style={{
            ...styles.button,
            opacity: isLoading || !isValid ? 0.5 : 1,
            cursor: isLoading || !isValid ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Generating...' : 'Generate Specification'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '0.5rem',
    padding: '1.5rem',
    marginBottom: '2rem',
  },
  formGroup: {
    marginBottom: '1rem',
  },
  label: {
    display: 'block',
    fontWeight: 600,
    marginBottom: '0.5rem',
    color: '#111827',
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid',
    borderRadius: '0.375rem',
    fontSize: '1rem',
    fontFamily: 'inherit',
    resize: 'vertical' as const,
    transition: 'border-color 0.2s',
  },
  footer: {
    marginTop: '0.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  wordCount: {
    fontSize: '0.875rem',
    fontWeight: 500,
  },
  error: {
    color: '#ef4444',
    fontSize: '0.875rem',
    marginTop: '0.25rem',
  },
  button: {
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    padding: '0.75rem 1.5rem',
    borderRadius: '0.375rem',
    fontWeight: 600,
    fontSize: '1rem',
    border: 'none',
    transition: 'background-color 0.2s',
  },
};
