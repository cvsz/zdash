import type { TradingScanResult } from "../../api/types";
import SectionCard from "../common/SectionCard";
import Button from "../common/Button";

type XauScannerPanelProps = {
  scanResult: TradingScanResult | null;
  loading?: boolean;
  onScan: () => void;
};

export default function XauScannerPanel({
  scanResult,
  loading = false,
  onScan,
}: XauScannerPanelProps) {
  return (
    <SectionCard
      title="XAUUSD M5 Scanner"
      subtitle="Damien Cross strategy engine"
      actions={
        <Button variant="secondary" onClick={onScan} disabled={loading}>
          {loading ? "Scanning..." : "Run Scan"}
        </Button>
      }
    >
      <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-3">
        <div className="rounded-md border border-slate-800 bg-slate-950/50 p-3">
          <p className="text-xs text-slate-400">Symbol</p>
          <p className="mt-1 font-semibold text-white">{scanResult?.symbol || "XAUUSD"}</p>
        </div>
        <div className="rounded-md border border-slate-800 bg-slate-950/50 p-3">
          <p className="text-xs text-slate-400">Timeframe</p>
          <p className="mt-1 font-semibold text-white">{scanResult?.timeframe || "M5"}</p>
        </div>
        <div className="rounded-md border border-slate-800 bg-slate-950/50 p-3">
          <p className="text-xs text-slate-400">Candles Analyzed</p>
          <p className="mt-1 font-semibold text-white">{scanResult?.candles_analyzed ?? 0}</p>
        </div>
      </div>
    </SectionCard>
  );
}
