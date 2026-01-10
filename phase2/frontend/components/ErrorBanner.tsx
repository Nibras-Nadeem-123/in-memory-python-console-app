'use client';

interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onDismiss, onRetry }: ErrorBannerProps) {
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" data-testid="error-banner">
      <span className="block sm:inline">{message}</span>
      <div className="mt-2 flex gap-2">
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 transition-colors"
          >
            Retry
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="bg-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-400 transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}
