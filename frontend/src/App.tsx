/**
 * Main application component.
 */

import { useState } from 'react';
import { useSpecGeneration } from './hooks/useSpecGeneration';
import { IntentInput } from './components/IntentInput';
import { SpecOutput } from './components/SpecOutput';
import { ErrorDisplay } from './components/ErrorDisplay';
import type { StructuredSpec } from './types/spec';

function App() {
  const [spec, setSpec] = useState<StructuredSpec | null>(null);
  const mutation = useSpecGeneration();

  const handleSubmit = (intent: string) => {
    mutation.mutate(intent, {
      onSuccess: (data) => {
        setSpec(data);
      },
    });
  };

  const handleRetry = () => {
    mutation.reset();
    setSpec(null);
  };

  return (
    <div className="container">
      <header style={{ marginBottom: '2rem' }}>
        <h1>Spec-Driven Development System</h1>
        <p className="text-secondary">
          Phase 1: Transform your intent into a structured specification
        </p>
      </header>

      <main>
        {/* Intent Input */}
        <IntentInput onSubmit={handleSubmit} isLoading={mutation.isPending} />

        {/* Loading State */}
        {mutation.isPending && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="spinner" style={{ margin: '0 auto' }}></div>
            <p style={{ marginTop: '1rem' }} className="text-secondary">
              Analyzing your intent and generating specification...
            </p>
          </div>
        )}

        {/* Error Display */}
        {mutation.isError && <ErrorDisplay error={mutation.error} onRetry={handleRetry} />}

        {/* Spec Output */}
        {spec && !mutation.isPending && <SpecOutput spec={spec} />}
      </main>

      <footer style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid #e5e7eb' }}>
        <p
          style={{
            textAlign: 'center',
            color: '#6b7280',
            fontSize: '0.875rem',
          }}
        >
          SDD Phase 1 - Intent to Specification | Backend API running on{' '}
          {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
        </p>
      </footer>
    </div>
  );
}

export default App;
