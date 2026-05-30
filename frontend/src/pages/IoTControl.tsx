import { useEffect, useMemo, useState } from "react";

import { getIoTStatus, powerCycleIoT, runIoTAction } from "../api/endpoints";
import type { IoTActionResult } from "../api/types";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import ConfirmDialog from "../components/common/ConfirmDialog";
import MetricCard from "../components/common/MetricCard";
import PageHeader from "../components/layout/PageHeader";
import { AGENT_NAME_BY_ID } from "../constants/agents";
import { useApi } from "../hooks/useApi";

const REQUIRED_TEXT = "CONFIRM_POWER_ACTION";
const actionOrder: Array<IoTActionResult["action"]> = ["status", "turn_on", "turn_off", "power_cycle"];

export default function IoTControl() {
  const statusState = useApi(getIoTStatus, []);

  const [latestResult, setLatestResult] = useState<IoTActionResult | null>(null);
  const [busyAction, setBusyAction] = useState<IoTActionResult["action"] | null>(null);
  const [typedConfirmation, setTypedConfirmation] = useState("");
  const [powerCycleConfirmOpen, setPowerCycleConfirmOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (statusState.data) {
      setLatestResult(statusState.data);
    }
  }, [statusState.data]);

  const activeResult = latestResult ?? statusState.data ?? null;

  const dryRun = activeResult?.dry_run !== false;
  const iotEnabled = activeResult?.ok === true;
  const deviceAlias = activeResult?.device_alias ?? "zdash-power-node";
  const realModeConfirmationSatisfied = typedConfirmation.trim() === REQUIRED_TEXT;

  const confirmationRequired = useMemo(() => {
    if (dryRun) {
      return "Power cycle confirmation dialog required; action remains simulated.";
    }
    return `Real mode requires typed confirmation text: ${REQUIRED_TEXT}.`;
  }, [dryRun]);

  async function performAction(action: IoTActionResult["action"]) {
    setBusyAction(action);
    setMessage(null);
    setError(null);
    try {
      if (action === "power_cycle") {
        const result = await powerCycleIoT(deviceAlias, true);
        setLatestResult(result);
      } else {
        const result = await runIoTAction({
          device_alias: deviceAlias,
          action,
          confirmation: dryRun || realModeConfirmationSatisfied,
        });
        setLatestResult(result);
      }
      setMessage(
        dryRun
          ? "Action simulated in IOT_DRY_RUN mode."
          : "Action submitted in guarded real mode.",
      );
    } catch (caught) {
      const text = caught instanceof Error ? caught.message : String(caught);
      setError(text);
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title="IoT Control"
        subtitle={`${AGENT_NAME_BY_ID.friday} owns scheduler-linked IoT safety orchestration.`}
        actions={<Badge variant={dryRun ? "success" : "warning"}>{dryRun ? "IOT_DRY_RUN" : "REAL_MODE"}</Badge>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="IoT Enabled" value={iotEnabled ? "YES" : "NO"} />
        <MetricCard label="IOT_DRY_RUN" value={dryRun ? "ON" : "OFF"} />
        <MetricCard label="Device Alias" value={deviceAlias} />
        <MetricCard label="Device Mode" value={dryRun ? "MOCK / SIMULATED" : "REAL / GUARDED"} />
      </div>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">Safety Conditions</h3>
        <p className="mt-2 text-sm text-text-secondary">{confirmationRequired}</p>
        {!dryRun ? (
          <label className="mt-3 block text-xs text-text-secondary">
            Required confirmation text
            <input
              className="mt-1 w-full rounded-md border border-border bg-canvas px-3 py-2 text-sm text-text-primary"
              value={typedConfirmation}
              onChange={(event) => setTypedConfirmation(event.target.value)}
              placeholder={REQUIRED_TEXT}
            />
          </label>
        ) : null}
      </section>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">Actions</h3>
        <p className="mt-1 text-xs text-text-dim">Available actions: status, turn_on, turn_off, power_cycle.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {actionOrder.map((action) => {
            const busy = busyAction === action;
            const blockedInRealMode = !dryRun && action !== "status" && !realModeConfirmationSatisfied;

            if (action === "power_cycle") {
              return (
                <Button
                  key={action}
                  variant="danger"
                  disabled={busy || blockedInRealMode}
                  onClick={() => setPowerCycleConfirmOpen(true)}
                >
                  {busy ? "Running..." : action}
                </Button>
              );
            }

            return (
              <Button
                key={action}
                variant="secondary"
                disabled={busy || blockedInRealMode}
                onClick={() => void performAction(action)}
              >
                {busy ? "Running..." : action}
              </Button>
            );
          })}
        </div>
      </section>

      {activeResult ? (
        <section className="rounded-card border border-border bg-panel p-4">
          <h3 className="text-sm font-semibold text-white">Latest Result</h3>
          <p className="mt-2 text-sm text-text-secondary">
            Action: <span className="font-semibold text-text-primary">{activeResult.action}</span>
          </p>
          <p className="mt-1 text-sm text-text-secondary">Message: {activeResult.message}</p>
          <p className="mt-1 text-sm text-text-secondary">
            Simulation state: {activeResult.dry_run ? "Simulated output" : "Real mode output"}
          </p>
        </section>
      ) : null}

      {message ? <p className="text-sm text-state-success">{message}</p> : null}
      {error ? <p className="text-sm text-state-danger">{error}</p> : null}

      <ConfirmDialog
        open={powerCycleConfirmOpen}
        title="Confirm power cycle"
        message="Power cycle requires confirmation. In dry-run mode the result remains simulated."
        confirmationText={dryRun ? undefined : REQUIRED_TEXT}
        confirmLabel="Confirm power cycle"
        onConfirm={() => {
          setPowerCycleConfirmOpen(false);
          void performAction("power_cycle");
        }}
        onCancel={() => setPowerCycleConfirmOpen(false)}
        isConfirming={busyAction === "power_cycle"}
      />
    </div>
  );
}
