import React from "react";

export function InvoiceHistory() {
  const invoices = [
    { id: "INV-001", date: "2024-05-01", amount: "$199.00", status: "Paid" },
    { id: "INV-002", date: "2024-04-01", amount: "$199.00", status: "Paid" },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="bg-neutral-800 text-neutral-300">
          <tr>
            <th className="p-3 font-medium">Invoice ID</th>
            <th className="p-3 font-medium">Date</th>
            <th className="p-3 font-medium">Amount</th>
            <th className="p-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-800">
          {invoices.map((inv) => (
            <tr key={inv.id} className="hover:bg-neutral-800/50">
              <td className="p-3">{inv.id}</td>
              <td className="p-3 text-neutral-400">{inv.date}</td>
              <td className="p-3">{inv.amount}</td>
              <td className="p-3">
                <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded text-xs">
                  {inv.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
