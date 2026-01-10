'use client';

import { useState, useEffect, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getTodoById, updateTodo } from '@/lib/api';
import { TodoForm, LoadingSpinner, ErrorBanner } from '@/components';
import { Todo } from '@/lib/types';

function EditTodoPage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);

  const [todo, setTodo] = useState<Todo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadTodo();
    }
  }, [id]);

  const loadTodo = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTodoById(id);
      setTodo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todo');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTodo = async (title: string, description?: string) => {
    try {
      await updateTodo(id, { title, description });
      router.push('/'); // Redirect to home page on success
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update todo');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <ErrorBanner
        message={error}
        onDismiss={() => setError(null)}
        onRetry={loadTodo}
      />
    );
  }

  return (
    <div className="min-h-screen px-4 py-8 bg-gray-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="mb-4 text-3xl font-bold text-gray-800">Edit Todo</h1>
        {todo && (
          <TodoForm
            initialTitle={todo.title}
            initialDescription={todo.description}
            onSubmit={handleUpdateTodo}
            onCancel={() => router.push('/')}
            submitLabel="Update Todo"
          />
        )}
      </div>
    </div>
  );
}

export default function EditTodoPageWithSuspense() {
    return (
        <Suspense fallback={<LoadingSpinner />}>
            <EditTodoPage />
        </Suspense>
    );
}
