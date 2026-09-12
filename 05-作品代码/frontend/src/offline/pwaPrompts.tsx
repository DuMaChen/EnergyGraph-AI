import { Download, RefreshCw } from 'lucide-react';
import { usePwaInstallPrompt } from './usePwaInstallPrompt';

export function InstallPromptButton() {
  const { canInstall, install } = usePwaInstallPrompt();
  if (!canInstall) return null;
  return (
    <button type="button" className="pwa-install-button" title="安装应用" aria-label="安装应用" onClick={() => void install()}>
      <Download size={15} />安装应用
    </button>
  );
}

interface UpdatePromptBannerProps {
  visible: boolean;
  onRefresh?: () => void;
}

export function UpdatePromptBanner({ visible, onRefresh }: UpdatePromptBannerProps) {
  if (!visible) return null;
  const refresh = onRefresh ?? (() => window.location.reload());
  return (
    <div className="pwa-update-banner" role="status" aria-live="polite">
      <RefreshCw size={16} />
      <span className="pwa-update-copy"><strong>发现新版本</strong><small>刷新后即可使用最新功能与内容。</small></span>
      <button type="button" className="button quiet pwa-update-action" onClick={refresh}>立即刷新</button>
    </div>
  );
}
