import React from "react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch() {
    // Error logged to console or service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 flex items-center justify-center bg-white z-20">
          <div className="p-8 bg-red-100 border border-red-400 rounded shadow-lg text-center">
            <h2 className="text-2xl font-bold text-red-700 mb-4">3D Background Failed to Load</h2>
            <p className="text-red-600 mb-2">{this.state.error?.message}</p>
            <p className="text-gray-700">The rest of the app is still usable.</p>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
