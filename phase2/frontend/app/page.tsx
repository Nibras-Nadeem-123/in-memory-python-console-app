'use client';

import { useState, useEffect } from 'react';
import { Todo, TodoFilters } from '../lib/types';
import { fetchTodos, createTodo, updateTodo, deleteTodo, updateTodoStatus } from '../lib/api';
import { TodoForm, FilterBar, LoadingSpinner, ErrorBanner } from '../components';
import TodoList from '@/components/TodoList';

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState<TodoFilters>({ status: 'all', search: '' });

  useEffect(() => {
    loadTodos();
  }, [filters]);

  const loadTodos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTodos(filters);
      setTodos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load todos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTodo = async (title: string, description?: string) => {
    try {
      await createTodo({ title, description });
      setShowForm(false);
      loadTodos();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create todo');
    }
  };

  const handleStatusChange = async (id: number, status: 'pending' | 'completed') => {
    try {
      await updateTodoStatus(id, status);
      loadTodos();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
    }
  };

  const handleDeleteTodo = async (id: number) => {
    if (!confirm('Are you sure you want to delete this todo?')) return;
    try {
      await deleteTodo(id);
      loadTodos();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete todo');
    }
  };

  const handleEditTodo = (id: number) => {
    // Navigate to edit page (simplified for now)
    window.location.href = `/todos/${id}/edit`;
  };

  return (
    <div className="min-h-screen px-4 py-8 bg-gray-100" data-testid="home-page">
      <div className="max-w-4xl mx-auto">
        <div className="p-6 mb-6 bg-white rounded-lg shadow-lg">
          <h1 className="mb-4 text-3xl font-bold text-gray-800">Todo List</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="w-full px-4 py-2 text-white transition-colors bg-blue-500 rounded-md md:w-auto hover:bg-blue-600"
            data-testid="add-todo-btn"
          >
            {showForm ? 'Cancel' : '+ Add Todo'}
          </button>
        </div>

        {showForm && (
          <TodoForm
            onSubmit={handleCreateTodo}
            onCancel={() => setShowForm(false)}
            submitLabel="Create Todo"
          />
        )}

        <FilterBar
          currentFilter={filters.status || 'all'}
          onFilterChange={(status) => setFilters({ ...filters, status })}
          searchQuery={filters.search || ''}
          onSearchChange={(search) => setFilters({ ...filters, search })}
        />

        {error && (
          <ErrorBanner
            message={error}
            onDismiss={() => setError(null)}
            onRetry={loadTodos}
          />
        )}

        {loading ? (
          <LoadingSpinner />
        ) : (
          <TodoList
            todos={todos}
            onStatusChange={handleStatusChange}
            onDelete={handleDeleteTodo}
            onEdit={handleEditTodo}
          />
        )}
      </div>
    </div>
  );
}
