import { Todo } from '../lib/types';

interface TodoItemProps {
  todo: Todo;
  onStatusChange: (id: number, status: 'pending' | 'completed') => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

export default function TodoItem({ todo, onStatusChange, onDelete, onEdit }: TodoItemProps) {
  return (
    <div className="p-4 mb-4 bg-white border-l-4 border-blue-500 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${todo.status === 'completed' ? 'line-through text-gray-500' : ''}`}>
            {todo.title}
          </h3>
          {todo.description && (
            <p className="mt-1 text-gray-600">{todo.description}</p>
          )}
          <div className="mt-2 text-sm text-gray-400">
            Created: {new Date(todo.created_at).toLocaleDateString()}
            {todo.status === 'completed' && (
              <span className="ml-4 font-medium text-green-600">Completed</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={todo.status === 'completed'}
            onChange={(e) => onStatusChange(todo.id, e.target.checked ? 'completed' : 'pending')}
            className="w-5 h-5 border-gray-300 rounded cursor-pointer"
            data-testid={`todo-checkbox-${todo.id}`}
          />
          <button
            onClick={() => onEdit(todo.id)}
            className="px-3 py-1 text-white transition-colors bg-blue-500 rounded hover:bg-blue-600"
            data-testid={`edit-btn-${todo.id}`}
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(todo.id)}
            className="px-3 py-1 text-white transition-colors bg-red-500 rounded hover:bg-red-600"
            data-testid={`delete-btn-${todo.id}`}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
