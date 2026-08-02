import type { VoiceSessionGrant } from "../../api/voice";

const PIPELINE_SAMPLE_RATE = 16_000;
const WORKLET_URL = "/voice-capture.worklet.js";

export type VoiceClientState =
  | "idle"
  | "connecting"
  | "connected"
  | "listening"
  | "processing"
  | "speaking"
  | "closed"
  | "error";

export type VoiceTranscriptEvent = {
  id: string;
  role: "user" | "assistant";
  text: string;
  partial: boolean;
};

export type VoiceClientCallbacks = {
  onState?: (state: VoiceClientState, message: string) => void;
  onTranscript?: (event: VoiceTranscriptEvent) => void;
  onError?: (error: Error) => void;
};

function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(binary);
}

function base64ToBytes(value: string): Uint8Array {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

export function resampleToPcm16(
  input: Float32Array,
  inputRate: number,
  outputRate = PIPELINE_SAMPLE_RATE,
): Uint8Array {
  if (!input.length || inputRate <= 0 || outputRate <= 0) return new Uint8Array();

  const ratio = inputRate / outputRate;
  const outputLength = Math.max(1, Math.floor(input.length / ratio));
  const output = new ArrayBuffer(outputLength * 2);
  const view = new DataView(output);

  for (let index = 0; index < outputLength; index += 1) {
    const position = index * ratio;
    const leftIndex = Math.floor(position);
    const rightIndex = Math.min(input.length - 1, leftIndex + 1);
    const fraction = position - leftIndex;
    const sample = input[leftIndex] * (1 - fraction) + input[rightIndex] * fraction;
    const clamped = Math.max(-1, Math.min(1, sample));
    view.setInt16(
      index * 2,
      clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff,
      true,
    );
  }

  return new Uint8Array(output);
}

export function pcm16ToFloat32(bytes: Uint8Array): Float32Array {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const samples = new Float32Array(Math.floor(bytes.byteLength / 2));
  for (let index = 0; index < samples.length; index += 1) {
    const value = view.getInt16(index * 2, true);
    samples[index] = value < 0 ? value / 0x8000 : value / 0x7fff;
  }
  return samples;
}

export class RealtimeVoiceClient {
  private readonly grant: VoiceSessionGrant;
  private readonly callbacks: VoiceClientCallbacks;
  private socket: WebSocket | null = null;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private captureNode: AudioWorkletNode | null = null;
  private muted = false;
  private sessionConfigured = false;
  private playhead = 0;
  private activeSources = new Set<AudioBufferSourceNode>();
  private assistantTranscript = new Map<string, string>();

  constructor(grant: VoiceSessionGrant, callbacks: VoiceClientCallbacks = {}) {
    this.grant = grant;
    this.callbacks = callbacks;
  }

  get isMuted(): boolean {
    return this.muted;
  }

  private setState(state: VoiceClientState, message: string): void {
    this.callbacks.onState?.(state, message);
  }

  private reportError(error: unknown): void {
    const normalized = error instanceof Error ? error : new Error("Voice session failed");
    this.setState("error", normalized.message);
    this.callbacks.onError?.(normalized);
  }

  async connect(): Promise<void> {
    if (this.socket || this.audioContext) throw new Error("Voice client is already connected");
    this.setState("connecting", "Requesting microphone access");

    try {
      await this.setupAudio();
      await this.openSocket();
    } catch (error) {
      this.reportError(error);
      await this.close();
      throw error;
    }
  }

  private async setupAudio(): Promise<void> {
    const audioContext = new AudioContext({ latencyHint: "interactive" });
    this.audioContext = audioContext;
    if (audioContext.state === "suspended") await audioContext.resume();
    await audioContext.audioWorklet.addModule(WORKLET_URL);

    const mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        channelCount: 1,
      },
    });
    this.mediaStream = mediaStream;

    const source = audioContext.createMediaStreamSource(mediaStream);
    const captureNode = new AudioWorkletNode(audioContext, "zdash-voice-capture");
    this.captureNode = captureNode;
    captureNode.port.onmessage = ({ data }: MessageEvent<unknown>) => {
      if (!(data instanceof Float32Array)) return;
      this.sendMicrophoneChunk(data);
    };

    source.connect(captureNode);
    const silentOutput = audioContext.createGain();
    silentOutput.gain.value = 0;
    captureNode.connect(silentOutput).connect(audioContext.destination);
  }

  private openSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(
        this.grant.websocket_url,
        [`zticket.${this.grant.ticket}`],
      );
      this.socket = socket;

      const failOpen = () => reject(new Error("Unable to open the voice WebSocket"));
      socket.addEventListener("error", failOpen, { once: true });
      socket.addEventListener(
        "open",
        () => {
          socket.removeEventListener("error", failOpen);
          this.setState("connecting", "Configuring realtime voice session");
          resolve();
        },
        { once: true },
      );
      socket.addEventListener("message", (event) => {
        void this.handleMessage(event.data);
      });
      socket.addEventListener("close", (event) => {
        this.sessionConfigured = false;
        this.stopPlayback();
        if (event.code === 1000) this.setState("closed", "Voice session closed");
        else this.reportError(new Error(`Voice WebSocket closed (${event.code})`));
      });
      socket.addEventListener("error", () => {
        this.reportError(new Error("Voice WebSocket transport error"));
      });
    });
  }

  private sendMicrophoneChunk(input: Float32Array): void {
    const socket = this.socket;
    const audioContext = this.audioContext;
    if (
      this.muted ||
      !this.sessionConfigured ||
      !audioContext ||
      !socket ||
      socket.readyState !== WebSocket.OPEN
    ) {
      return;
    }

    const bytes = resampleToPcm16(input, audioContext.sampleRate);
    if (!bytes.length) return;
    socket.send(
      JSON.stringify({
        type: "input_audio_buffer.append",
        audio: bytesToBase64(bytes),
      }),
    );
  }

  private async handleMessage(raw: string | ArrayBuffer | Blob): Promise<void> {
    let text: string;
    if (typeof raw === "string") text = raw;
    else if (raw instanceof Blob) text = await raw.text();
    else text = new TextDecoder().decode(raw);

    let event: Record<string, unknown>;
    try {
      event = JSON.parse(text) as Record<string, unknown>;
    } catch {
      return;
    }

    const type = typeof event.type === "string" ? event.type : "";
    switch (type) {
      case "session.created":
        this.send({
          type: "session.update",
          session: {
            type: "realtime",
            instructions: this.grant.instructions,
          },
        });
        this.sessionConfigured = true;
        this.setState("connected", "Connected — speak naturally");
        break;
      case "input_audio_buffer.speech_started":
        this.stopPlayback();
        this.setState("listening", "Listening");
        break;
      case "input_audio_buffer.speech_stopped":
        this.setState("processing", "Processing");
        break;
      case "conversation.item.input_audio_transcription.delta":
      case "conversation.item.input_audio_transcription.completed": {
        const transcript =
          typeof event.transcript === "string"
            ? event.transcript
            : typeof event.delta === "string"
              ? event.delta
              : "";
        if (transcript) {
          this.callbacks.onTranscript?.({
            id: typeof event.item_id === "string" ? event.item_id : crypto.randomUUID(),
            role: "user",
            text: transcript,
            partial: type.endsWith(".delta"),
          });
        }
        break;
      }
      case "response.audio.delta":
      case "response.output_audio.delta":
        if (typeof event.delta === "string") this.queueAudio(event.delta);
        this.setState("speaking", "Assistant speaking");
        break;
      case "response.audio_transcript.delta":
      case "response.output_audio_transcript.delta": {
        const responseId =
          typeof event.response_id === "string" ? event.response_id : "assistant";
        const delta = typeof event.delta === "string" ? event.delta : "";
        if (delta) {
          const textValue = `${this.assistantTranscript.get(responseId) ?? ""}${delta}`;
          this.assistantTranscript.set(responseId, textValue);
          this.callbacks.onTranscript?.({
            id: responseId,
            role: "assistant",
            text: textValue,
            partial: true,
          });
        }
        break;
      }
      case "response.audio_transcript.done":
      case "response.output_audio_transcript.done": {
        const responseId =
          typeof event.response_id === "string" ? event.response_id : "assistant";
        const transcript =
          typeof event.transcript === "string"
            ? event.transcript
            : this.assistantTranscript.get(responseId) ?? "";
        this.assistantTranscript.delete(responseId);
        if (transcript) {
          this.callbacks.onTranscript?.({
            id: responseId,
            role: "assistant",
            text: transcript,
            partial: false,
          });
        }
        break;
      }
      case "response.done":
        this.setState("connected", "Connected — speak naturally");
        break;
      case "error": {
        const detail = event.error;
        const message =
          detail && typeof detail === "object" && "message" in detail
            ? String((detail as { message: unknown }).message)
            : "Voice runtime error";
        this.reportError(new Error(message));
        break;
      }
      default:
        break;
    }
  }

  private queueAudio(base64Audio: string): void {
    const audioContext = this.audioContext;
    if (!audioContext || !base64Audio) return;

    const samples = pcm16ToFloat32(base64ToBytes(base64Audio));
    if (!samples.length) return;
    const buffer = audioContext.createBuffer(1, samples.length, PIPELINE_SAMPLE_RATE);
    buffer.copyToChannel(samples, 0);

    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContext.destination);
    const startAt = Math.max(audioContext.currentTime + 0.02, this.playhead);
    source.start(startAt);
    this.playhead = startAt + buffer.duration;
    this.activeSources.add(source);
    source.addEventListener("ended", () => this.activeSources.delete(source), {
      once: true,
    });
  }

  private send(payload: object): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  setMuted(muted: boolean): void {
    this.muted = muted;
    this.setState(
      muted ? "idle" : "connected",
      muted ? "Microphone muted" : "Connected — speak naturally",
    );
  }

  cancelResponse(): void {
    this.send({ type: "response.cancel" });
    this.stopPlayback();
    this.setState("connected", "Response cancelled");
  }

  private stopPlayback(): void {
    for (const source of this.activeSources) {
      try {
        source.stop();
      } catch {
        // Source already completed.
      }
    }
    this.activeSources.clear();
    this.playhead = this.audioContext?.currentTime ?? 0;
  }

  async close(): Promise<void> {
    this.sessionConfigured = false;
    this.stopPlayback();

    const socket = this.socket;
    this.socket = null;
    if (socket && socket.readyState < WebSocket.CLOSING) {
      socket.close(1000, "client_stop");
    }

    this.captureNode?.disconnect();
    this.captureNode = null;
    for (const track of this.mediaStream?.getTracks() ?? []) track.stop();
    this.mediaStream = null;

    const audioContext = this.audioContext;
    this.audioContext = null;
    if (audioContext && audioContext.state !== "closed") await audioContext.close();

    this.muted = false;
    this.setState("closed", "Voice session closed");
  }
}
