import { Todo } from '../lib/types';
import TodoItem from './TodoItem';

interface TodoListProps {
  todos: Todo[];
  onStatusChange: (id: number, status: 'pending' | 'completed') => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

export default function TodoList({ todos, onStatusChange, onDelete, onEdit }: TodoListProps) {
  if (todos.length === 0) {
    return (
      <div className="py-12 text-center text-gray-500">
        <p className="text-lg">No todos found</p>
        <p className="mt-2 text-sm">Create your first todo to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onStatusChange={onStatusChange}
          onDelete={onDelete}
          onEdit={onEdit}
        />
      ))}
    </div>
  );
}
