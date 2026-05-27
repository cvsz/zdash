import type { TradingSignal } from "../../api/types";
import DataTable from "../common/DataTable";
import Badge from "../common/Badge";

type SignalTableProps = {
  signals: TradingSignal[];
  onSelect?: (signal: TradingSignal) => void;
};

export default function SignalTable({ signals, onSelect }: SignalTableProps) {
  return (
    <DataTable
      columns={[
        {
          key: "symbol",
          header: "Symbol",
          render: (row) => row.symbol,
        },
        {
          key: "timeframe",
          header: "TF",
          render: (row) => row.timeframe,
        },
        {
          key: "direction",
          header: "Direction",
          render: (row) => (
            <Badge
              variant={
                (row.direction || row.side) === "buy"
                  ? "success"
                  : (row.direction || row.side) === "sell"
                    ? "danger"
                    : "muted"
              }
            >
              {(row.direction || row.side || "hold").toUpperCase()}
            </Badge>
          ),
        },
        {
          key: "confidence",
          header: "Confidence",
          render: (row) => `${(row.confidence * 100).toFixed(1)}%`,
        },
        {
          key: "actions",
          header: "Action",
          render: (row) => (
            <button
              type="button"
              className="rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-200 hover:bg-slate-800"
              onClick={() => onSelect?.(row)}
            >
              Select
            </button>
          ),
        },
      ]}
      rows={signals}
      rowKey={(row, index) => row.id || `${row.symbol}-${row.timeframe}-${index}`}
      emptyMessage="No signals available."
    />
  );
}
