import { useEffect, useMemo, useRef, useState } from "react";
import { Ban, Mic, MicOff, ShieldCheck, Square, Trash2 } from "lucide-react";

import { createVoiceSession, getVoiceIntegrationStatus, type VoiceIntegrationStatus } from "../api/voice";
import SectionCard from "../components/common/SectionCard";
import PageHeader from "../components/layout/PageHeader";
import {
  RealtimeVoiceClient,
  type VoiceClientState,
  type VoiceTranscriptEvent,
} from "../features/voice/RealtimeVoiceClient";
import { useT } from "../hooks/useT";

type TranscriptEntry = VoiceTranscriptEvent & { updatedAt: number };

const copy = {
  en: {
    title: "Realtime Voice Agent",
    subtitle: "Talk to the z-platform local voice runtime through the authenticated zDash control plane.",
    runtime: "Runtime connection",
    runtimeSubtitle: "zDash brokers a short-lived ticket; provider and service credentials never enter the browser.",
    enabled: "Enabled",
    configured: "Configured",
    model: "Model",
    instructions: "Assistant instructions",
    instructionsDefault: "You are a concise, helpful voice assistant. Reply in the user's language.",
    start: "Start voice",
    stop: "Stop",
    mute: "Mute",
    unmute: "Unmute",
    cancel: "Cancel response",
    transcript: "Live transcript",
    transcriptSubtitle: "Transcript state is browser-local and is cleared when the page reloads.",
    clear: "Clear",
    empty: "Start a voice session and speak naturally.",
    user: "You",
    assistant: "Assistant",
    privacy: "Privacy and safety boundary",
    privacyBody: "Microphone audio is streamed only to the configured z-platform voice gateway. zDash sends tenant and authenticated user identity to obtain a single-use ticket. The browser never receives Z_PLATFORM_SERVICE_TOKEN or provider keys.",
    loading: "Checking voice integration",
    ready: "Ready to request microphone access",
    unavailable: "Voice integration is disabled or incomplete. Configure the backend environment before starting a session.",
  },
  th: {
    title: "เอเจนต์เสียงแบบเรียลไทม์",
    subtitle: "สนทนากับระบบเสียงภายใน z-platform ผ่าน control plane ที่ยืนยันตัวตนของ zDash",
    runtime: "การเชื่อมต่อระบบเสียง",
    runtimeSubtitle: "zDash เป็นผู้ขอ ticket อายุสั้น โดย credential ของระบบและผู้ให้บริการจะไม่ถูกส่งเข้า browser",
    enabled: "เปิดใช้งาน",
    configured: "ตั้งค่าครบ",
    model: "โมเดล",
    instructions: "คำสั่งสำหรับผู้ช่วย",
    instructionsDefault: "คุณคือผู้ช่วยเสียงที่กระชับและเป็นประโยชน์ ให้ตอบด้วยภาษาของผู้ใช้",
    start: "เริ่มสนทนาด้วยเสียง",
    stop: "หยุด",
    mute: "ปิดไมค์",
    unmute: "เปิดไมค์",
    cancel: "ยกเลิกคำตอบ",
    transcript: "บทสนทนาแบบสด",
    transcriptSubtitle: "ข้อความสนทนาเก็บอยู่ใน browser และจะถูกล้างเมื่อโหลดหน้าใหม่",
    clear: "ล้าง",
    empty: "เริ่ม session แล้วพูดได้ตามปกติ",
    user: "คุณ",
    assistant: "ผู้ช่วย",
    privacy: "ขอบเขตความเป็นส่วนตัวและความปลอดภัย",
    privacyBody: "เสียงจากไมโครโฟนจะส่งไปยัง z-platform voice gateway ที่กำหนดไว้เท่านั้น zDash ส่ง tenant และตัวตนผู้ใช้ที่ผ่านการยืนยันเพื่อขอ ticket แบบใช้ครั้งเดียว Browser จะไม่ได้รับ Z_PLATFORM_SERVICE_TOKEN หรือ provider key",
    loading: "กำลังตรวจสอบระบบเสียง",
    ready: "พร้อมขอสิทธิ์ใช้งานไมโครโฟน",
    unavailable: "ระบบเสียงยังปิดอยู่หรือตั้งค่าไม่ครบ กรุณาตั้งค่า environment ของ backend ก่อนเริ่ม session",
  },
};

export default function VoiceAgent() {
  const { currentLang } = useT();
  const text = currentLang.startsWith("th") ? copy.th : copy.en;
  const clientRef = useRef<RealtimeVoiceClient | null>(null);
  const [integration, setIntegration] = useState<VoiceIntegrationStatus | null>(null);
  const [instructions, setInstructions] = useState(text.instructionsDefault);
  const [clientState, setClientState] = useState<VoiceClientState>("idle");
  const [statusMessage, setStatusMessage] = useState(text.loading);
  const [transcripts, setTranscripts] = useState<TranscriptEntry[]>([]);
  const [starting, setStarting] = useState(false);
  const [muted, setMuted] = useState(false);

  useEffect(() => {
    let active = true;
    void getVoiceIntegrationStatus()
      .then((result) => {
        if (!active) return;
        setIntegration(result);
        setStatusMessage(result.enabled && result.configured ? text.ready : text.unavailable);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setStatusMessage(error instanceof Error ? error.message : text.unavailable);
      });
    return () => {
      active = false;
      void clientRef.current?.close();
      clientRef.current = null;
    };
  }, [text.ready, text.unavailable]);

  useEffect(() => {
    if (clientState === "idle" && !clientRef.current) {
      setInstructions(text.instructionsDefault);
    }
  }, [clientState, text.instructionsDefault]);

  const connected = useMemo(
    () => !["idle", "closed", "error"].includes(clientState),
    [clientState],
  );

  function handleTranscript(event: VoiceTranscriptEvent) {
    setTranscripts((current) => {
      const index = current.findIndex(
        (item) => item.id === event.id && item.role === event.role,
      );
      const next = { ...event, updatedAt: Date.now() };
      if (index === -1) return [...current, next];
      const copyEntries = [...current];
      copyEntries[index] = next;
      return copyEntries;
    });
  }

  async function startVoice() {
    if (starting || connected) return;
    setStarting(true);
    setStatusMessage(text.loading);
    try {
      const grant = await createVoiceSession(instructions.trim());
      const client = new RealtimeVoiceClient(grant, {
        onState: (state, message) => {
          setClientState(state);
          setStatusMessage(message);
        },
        onTranscript: handleTranscript,
        onError: (error) => setStatusMessage(error.message),
      });
      clientRef.current = client;
      await client.connect();
    } catch (error) {
      setClientState("error");
      setStatusMessage(error instanceof Error ? error.message : text.unavailable);
      clientRef.current = null;
    } finally {
      setStarting(false);
    }
  }

  async function stopVoice() {
    const client = clientRef.current;
    clientRef.current = null;
    if (client) await client.close();
    setClientState("closed");
    setMuted(false);
  }

  function toggleMute() {
    const client = clientRef.current;
    if (!client) return;
    const next = !muted;
    client.setMuted(next);
    setMuted(next);
  }

  return (
    <div className="space-y-6">
      <PageHeader title={text.title} subtitle={text.subtitle} />

      <SectionCard title={text.runtime} subtitle={text.runtimeSubtitle}>
        <div className="grid gap-3 text-sm md:grid-cols-3">
          <div className="rounded-lg border border-border bg-canvas/50 p-3">
            <p className="text-xs text-text-dim">{text.enabled}</p>
            <p className="mt-1 font-semibold text-text-primary">{String(integration?.enabled ?? false)}</p>
          </div>
          <div className="rounded-lg border border-border bg-canvas/50 p-3">
            <p className="text-xs text-text-dim">{text.configured}</p>
            <p className="mt-1 font-semibold text-text-primary">{String(integration?.configured ?? false)}</p>
          </div>
          <div className="rounded-lg border border-border bg-canvas/50 p-3">
            <p className="text-xs text-text-dim">{text.model}</p>
            <p className="mt-1 break-all font-semibold text-text-primary">{integration?.model ?? "—"}</p>
          </div>
        </div>

        <label className="mt-4 block text-sm text-text-secondary">
          <span className="font-medium">{text.instructions}</span>
          <textarea
            className="mt-2 min-h-28 w-full rounded-lg border border-border bg-canvas px-3 py-2 text-text-primary outline-none focus:border-accent-cyan"
            value={instructions}
            onChange={(event) => setInstructions(event.target.value)}
            disabled={connected || starting}
            maxLength={8000}
          />
        </label>

        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void startVoice()}
            disabled={starting || connected || !integration?.enabled || !integration.configured}
            className="inline-flex items-center gap-2 rounded-lg bg-accent-cyan px-4 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Mic size={16} /> {text.start}
          </button>
          <button
            type="button"
            onClick={toggleMute}
            disabled={!connected}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm text-text-primary disabled:opacity-50"
          >
            {muted ? <Mic size={16} /> : <MicOff size={16} />}
            {muted ? text.unmute : text.mute}
          </button>
          <button
            type="button"
            onClick={() => clientRef.current?.cancelResponse()}
            disabled={!connected}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm text-text-primary disabled:opacity-50"
          >
            <Ban size={16} /> {text.cancel}
          </button>
          <button
            type="button"
            onClick={() => void stopVoice()}
            disabled={!connected}
            className="inline-flex items-center gap-2 rounded-lg border border-red-500/40 px-4 py-2 text-sm text-red-300 disabled:opacity-50"
          >
            <Square size={16} /> {text.stop}
          </button>
        </div>

        <div
          className="mt-4 rounded-lg border border-border bg-canvas/60 px-3 py-2 text-sm text-text-secondary"
          role="status"
          aria-live="polite"
        >
          <span className="mr-2 inline-block h-2 w-2 rounded-full bg-accent-cyan" />
          {statusMessage}
        </div>
      </SectionCard>

      <SectionCard
        title={text.transcript}
        subtitle={text.transcriptSubtitle}
        actions={
          <button
            type="button"
            onClick={() => setTranscripts([])}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-xs text-text-secondary"
          >
            <Trash2 size={14} /> {text.clear}
          </button>
        }
      >
        {transcripts.length === 0 ? (
          <div className="grid min-h-36 place-items-center text-sm text-text-dim">{text.empty}</div>
        ) : (
          <ol className="max-h-[420px] space-y-3 overflow-auto" aria-live="polite">
            {transcripts.map((entry) => (
              <li
                key={`${entry.role}-${entry.id}`}
                className={`rounded-lg border p-3 ${
                  entry.role === "assistant"
                    ? "border-accent-cyan/30 bg-accent-cyan/5"
                    : "border-violet-400/30 bg-violet-400/5"
                }`}
              >
                <div className="mb-1 flex items-center justify-between gap-3 text-xs text-text-dim">
                  <strong className="text-text-secondary">
                    {entry.role === "assistant" ? text.assistant : text.user}
                  </strong>
                  {entry.partial ? <span>…</span> : null}
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6 text-text-primary">{entry.text}</p>
              </li>
            ))}
          </ol>
        )}
      </SectionCard>

      <SectionCard title={text.privacy}>
        <div className="flex gap-3 text-sm leading-6 text-text-secondary">
          <ShieldCheck className="mt-0.5 shrink-0 text-accent-cyan" size={20} />
          <p>{text.privacyBody}</p>
        </div>
      </SectionCard>
    </div>
  );
}
