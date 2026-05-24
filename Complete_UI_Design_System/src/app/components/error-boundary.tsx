import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    // TODO: send to error tracking (e.g. Sentry) when configured
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="min-h-screen flex items-center justify-center px-6 bg-[#0a0a0f] text-white">
          <div className="max-w-md w-full text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#EF4444] to-[#F59E0B] rounded-2xl mx-auto mb-6 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold mb-2">Something went wrong</h1>
            <p className="text-gray-400 mb-6">
              An unexpected error occurred. Please try again or refresh the page.
            </p>
            {import.meta.env.DEV && this.state.error && (
              <pre className="text-left text-xs bg-white/5 border border-white/10 rounded-lg p-4 mb-6 overflow-auto max-h-40">
                {this.state.error.message}
              </pre>
            )}
            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleReset}
                className="px-6 py-3 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                Try Again
              </button>
              <button
                onClick={() => (window.location.href = '/')}
                className="px-6 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
