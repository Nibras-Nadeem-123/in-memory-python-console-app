import {
  Todo,
  TodoCreate,
  TodoUpdate,
  TodoStatusUpdate,
  TodoFilters,
  ErrorResponse
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.error || error.detail || 'Request failed');
  }
  return response.json();
}

export async function fetchTodos(filters: TodoFilters = {}): Promise<Todo[]> {
  const params = new URLSearchParams();
  if (filters.status && filters.status !== 'all') {
    params.append('status', filters.status);
  }
  if (filters.search) {
    params.append('search', filters.search);
  }
  params.append('limit', String(filters.limit || 50));
  params.append('offset', String(filters.offset || 0));

  const response = await fetch(`${API_URL}/api/todos?${params.toString()}`);
  return handleResponse<Todo[]>(response);
}

export async function getTodoById(id: number): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/todos/${id}`);
  return handleResponse<Todo>(response);
}


export async function createTodo(todo: TodoCreate): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  });
  return handleResponse<Todo>(response);
}

export async function updateTodo(id: number, todo: TodoUpdate): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(todo),
  });
  return handleResponse<Todo>(response);
}

export async function deleteTodo(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/todos/${id}`, {
    method: 'DELETE',
  });
  return handleResponse<void>(response);
}

export async function updateTodoStatus(id: number, status: string): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/todos/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  return handleResponse<Todo>(response);
}
