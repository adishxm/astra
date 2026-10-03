import React, { Component } from 'react';
import ErrorBanner from './ErrorBanner';
import { getErrorMessage } from '../../api/client';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // In dev, log error info
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an unhandled error:', error, errorInfo);
    }
  }

  handleReload = () => {
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 'var(--space-2xl)', maxWidth: '800px', margin: '0 auto' }}>
          <ErrorBanner
            title="Application Error"
            message={getErrorMessage(this.state.error)}
            onRetry={this.handleReload}
          />
        </div>
      );
    }

    return this.props.children;
  }
}
