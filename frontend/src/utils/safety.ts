type ApprovalLike = {
  approval_required?: boolean;
  approved?: boolean;
};

export function isLiveTradingBlocked(liveTradingEnabled = false): boolean {
  return !liveTradingEnabled;
}

export function requiresApproval(item: ApprovalLike): boolean {
  return Boolean(item.approval_required);
}

export function canPublishContent(item: ApprovalLike): boolean {
  if (!requiresApproval(item)) {
    return true;
  }
  return Boolean(item.approved);
}

export function canRunIoTAction(
  dryRunMode: boolean,
  confirmationSatisfied = false,
): boolean {
  if (dryRunMode) {
    return true;
  }
  return confirmationSatisfied;
}

export function getSafetyBannerText(): string {
  return "Safety mode active: dry-run, approval gates, and guardrails are enabled.";
}
