import React from 'react';

interface EmptyStateProps {
  message?: string;
}

export default function EmptyState({ message = "No todos found" }: EmptyStateProps) {
  return (
    <div className="text-center py-12 bg-gray-50 rounded-lg" data-testid="empty-state">
      <div className="text-6xl mb-4">📝</div>
      <p className="text-xl text-gray-600">{message}</p>
      <p className="text-sm text-gray-400 mt-2">
        {message === "No todos found"
          ? "Create your first todo to get started"
          : "Try adjusting your filters or search"}
      </p>
    </div>
  );
}
