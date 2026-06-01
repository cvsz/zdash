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
import { useT } from "../hooks/useT";

const REQUIRED_TEXT = "CONFIRM_POWER_ACTION";
const actionOrder: Array<IoTActionResult["action"]> = ["status", "turn_on", "turn_off", "power_cycle"];

export default function IoTControl() {
  const { t } = useT();
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
      return t('iot.confirmation_required_dry_run');
    }
    return t('iot.confirmation_required_real', { text: REQUIRED_TEXT });
  }, [t, dryRun]);

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
          ? t('iot.action_simulated')
          : t('iot.action_submitted_guarded'),
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
        title={t('iot.title')}
        subtitle={t('iot.panel_subtitle', { agent: AGENT_NAME_BY_ID.friday })}
        actions={<Badge variant={dryRun ? "success" : "warning"}>{dryRun ? t('iot.iot_dry_run') : t('iot.real_guarded')}</Badge>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label={t('iot.iot_enabled')} value={iotEnabled ? t('common.yes') : t('common.no')} />
        <MetricCard label={t('iot.iot_dry_run')} value={dryRun ? t('common.on') : t('common.off')} />
        <MetricCard label={t('iot.device_alias')} value={deviceAlias} />
        <MetricCard label={t('iot.device_mode')} value={dryRun ? t('iot.mock_simulated') : t('iot.real_guarded')} />
      </div>

      <section className="rounded-card border border-border bg-panel p-4">
        <h3 className="text-sm font-semibold text-white">{t('iot.safety_conditions')}</h3>
        <p className="mt-2 text-sm text-text-secondary">{confirmationRequired}</p>
        {!dryRun ? (
          <label className="mt-3 block text-xs text-text-secondary">
            {t('iot.required_confirmation_text')}
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
        <h3 className="text-sm font-semibold text-white">{t('iot.actions')}</h3>
        <p className="mt-1 text-xs text-text-dim">{t('iot.actions_subtitle')}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {actionOrder.map((action) => {
            const busy = busyAction === action;
            const blockedInRealMode = !dryRun && action !== "status" && !realModeConfirmationSatisfied;

            const actionLabel = action === "turn_on" ? t('iot.power_on') : action === "turn_off" ? t('iot.power_off') : action === "power_cycle" ? t('iot.reboot') : t('common.status');

            if (action === "power_cycle") {
              return (
                <Button
                  key={action}
                  variant="danger"
                  disabled={busy || blockedInRealMode}
                  onClick={() => setPowerCycleConfirmOpen(true)}
                >
                  {busy ? t('iot.running') : actionLabel}
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
                {busy ? t('iot.running') : actionLabel}
              </Button>
            );
          })}
        </div>
      </section>

      {activeResult ? (
        <section className="rounded-card border border-border bg-panel p-4">
          <h3 className="text-sm font-semibold text-white">{t('iot.latest_result')}</h3>
          <p className="mt-2 text-sm text-text-secondary">
            {t('iot.action_label')}: <span className="font-semibold text-text-primary">{activeResult.action}</span>
          </p>
          <p className="mt-1 text-sm text-text-secondary">{t('iot.message_label')}: {activeResult.message}</p>
          <p className="mt-1 text-sm text-text-secondary">
            {t('iot.simulation_state')}: {activeResult.dry_run ? t('iot.simulated_output') : t('iot.real_mode_output')}
          </p>
        </section>
      ) : null}

      {message ? <p className="text-sm text-state-success">{message}</p> : null}
      {error ? <p className="text-sm text-state-danger">{error}</p> : null}

      <ConfirmDialog
        open={powerCycleConfirmOpen}
        title={t('iot.confirm_power_cycle')}
        message={t('iot.confirm_power_cycle_message')}
        confirmationText={dryRun ? undefined : REQUIRED_TEXT}
        confirmLabel={t('iot.confirm_power_cycle_label')}
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
