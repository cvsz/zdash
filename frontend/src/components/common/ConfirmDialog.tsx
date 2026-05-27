import { useEffect, useState } from "react";

import Button from "./Button";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  message: string;
  confirmationText?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isConfirming?: boolean;
};

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmationText,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
  isConfirming = false,
}: ConfirmDialogProps) {
  const [typedText, setTypedText] = useState("");

  useEffect(() => {
    if (!open) {
      setTypedText("");
    }
  }, [open]);

  if (!open) {
    return null;
  }

  const confirmationSatisfied =
    !confirmationText || typedText.trim() === confirmationText.trim();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4">
      <div className="w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-2xl shadow-slate-950/40">
        <h4 className="text-base font-semibold text-white">{title}</h4>
        <p className="mt-2 text-sm text-slate-300">{message}</p>

        {confirmationText ? (
          <div className="mt-4">
            <p className="mb-2 text-xs text-slate-400">
              Type <span className="font-semibold text-slate-200">{confirmationText}</span> to confirm.
            </p>
            <input
              value={typedText}
              onChange={(event) => setTypedText(event.target.value)}
              className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-500/60 transition focus:ring"
              placeholder={confirmationText}
            />
          </div>
        ) : null}

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button
            variant="danger"
            onClick={onConfirm}
            disabled={!confirmationSatisfied || isConfirming}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
