export interface Todo {
  id: number;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
  description?: string;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
  status?: 'pending' | 'completed';
}

export interface TodoStatusUpdate {
  status: 'pending' | 'completed';
}

export interface TodoFilters {
  status?: 'all' | 'pending' | 'completed';
  search?: string;
  limit?: number;
  offset?: number;
}

export interface ErrorResponse {
  error: string;
  field?: string;
  message?: string;
  detail?: string;
}
