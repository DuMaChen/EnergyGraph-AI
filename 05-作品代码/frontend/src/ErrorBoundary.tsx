import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { reportClientError } from './lib/observability';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  errorId: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, errorId: '' };

  static getDerivedStateFromError(): State {
    return { hasError: true, errorId: '' };
  }

  componentDidCatch(error: unknown, _info: ErrorInfo): void {
    const record = reportClientError(error, 'render');
    this.setState({ hasError: true, errorId: record.id });
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <main className="error-boundary" role="alert">
        <div className="error-boundary-icon"><AlertTriangle size={25} /></div>
        <p className="eyebrow">课程平台</p>
        <h1>页面暂时无法显示</h1>
        <p>当前页面遇到未预期错误，已保留脱敏诊断记录。请重新加载后继续。</p>
        <div className="error-boundary-actions">
          <button className="button primary" onClick={() => window.location.reload()}><RefreshCw size={16} />重新加载</button>
          <small>错误编号：{this.state.errorId || '记录中'}</small>
        </div>
      </main>
    );
  }
}
