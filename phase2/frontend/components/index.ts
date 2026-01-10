import { Todo } from '../types';

interface TodoListProps {
  todos: Todo[];
  onStatusChange: (id: number, status: 'pending' | 'completed') => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

export { default as TodoItem } from './TodoItem';
export { default as TodoForm } from './TodoForm';
export { default as FilterBar } from './FilterBar';
export { default as LoadingSpinner } from './LoadingSpinner';
export { default as ErrorBanner } from './ErrorBanner';
export { default as EmptyState } from './EmptyState';
