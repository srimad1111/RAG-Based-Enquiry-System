import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an unhandled error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6 bg-canvas-base text-white">
          <div className="max-w-lg w-full bg-canvas-card rounded-2xl border border-roseAccent/30 shadow-dark-elevated p-6 text-white space-y-4">
            <div className="flex items-center space-x-3 text-roseAccent">
              <AlertTriangle className="w-8 h-8 flex-shrink-0" />
              <div>
                <h2 className="text-base font-bold text-white">Application Encountered an Error</h2>
                <p className="text-xs text-slate-400">The component failed to render cleanly.</p>
              </div>
            </div>

            <div className="bg-canvas-void border border-white/[0.08] rounded-xl p-3 text-xs font-mono text-roseAccent-light overflow-auto max-h-40">
              {this.state.error?.toString() || 'Unknown runtime error'}
            </div>

            <div className="flex items-center space-x-3 pt-2">
              <button
                onClick={this.handleReload}
                className="flex items-center space-x-2 px-4 py-2 bg-violetAccent hover:bg-violetAccent-hover text-white rounded-xl text-xs font-semibold shadow-glow-violet transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reload Page</span>
              </button>
              <button
                onClick={this.handleReset}
                className="px-4 py-2 bg-canvas-void hover:bg-white/[0.08] text-slate-300 rounded-xl text-xs font-semibold border border-white/[0.08] transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
