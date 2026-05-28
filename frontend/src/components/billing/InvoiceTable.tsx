import React from "react";
import { Invoice } from "../../api/types";

interface InvoiceTableProps {
  invoices: Invoice[];
}

export function InvoiceTable({ invoices }: InvoiceTableProps) {
  if (invoices.length === 0) {
    return (
      <div className="p-8 text-center text-neutral-500 text-sm border border-neutral-800 rounded-xl bg-neutral-950/20">
        No invoices found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-neutral-800 bg-neutral-950/20">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-neutral-850 bg-neutral-900/10 text-neutral-400 text-xs font-semibold uppercase tracking-wider">
            <th className="p-4">Invoice #</th>
            <th className="p-4">Date</th>
            <th className="p-4">Amount</th>
            <th className="p-4">Status</th>
            <th className="p-4 text-right">Receipt</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-850 text-sm text-neutral-300">
          {invoices.map((inv) => (
            <tr key={inv.id} className="hover:bg-neutral-900/10">
              <td className="p-4 font-mono font-medium text-white">{inv.number}</td>
              <td className="p-4">{new Date(inv.created_at).toLocaleDateString()}</td>
              <td className="p-4 font-mono">
                ${inv.amount.toFixed(2)} {inv.currency.toUpperCase()}
              </td>
              <td className="p-4">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    inv.status === "paid"
                      ? "text-green-400 bg-green-500/10"
                      : inv.status === "open"
                      ? "text-amber-400 bg-amber-500/10"
                      : "text-neutral-400 bg-neutral-500/10"
                  }`}
                >
                  {inv.status}
                </span>
              </td>
              <td className="p-4 text-right">
                {inv.hosted_invoice_url || inv.pdf_url ? (
                  <a
                    href={inv.hosted_invoice_url || inv.pdf_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-violet-400 hover:text-violet-300 underline font-medium text-xs transition duration-150"
                  >
                    Download PDF
                  </a>
                ) : (
                  <span className="text-neutral-600 text-xs">Unavailable</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
