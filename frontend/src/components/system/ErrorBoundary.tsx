import { Component, type ErrorInfo, type ReactNode } from 'react';

type Props = { children: ReactNode };
type State = { hasError: boolean };

export default class ErrorBoundary extends Component<Props, State> {
  public constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  public static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    if (import.meta.env.DEV) {
      console.error('Dashboard runtime error boundary caught an error', error, errorInfo);
    }
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="m-6 rounded border border-rose-700 bg-rose-950 p-4 text-rose-100">
          Dashboard encountered an unexpected error. Refresh the page to recover.
        </div>
      );
    }

    return this.props.children;
  }
}
