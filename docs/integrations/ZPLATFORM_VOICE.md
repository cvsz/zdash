# z-platform Realtime Voice Integration

## Purpose

zDash provides the authenticated operations dashboard and control surface. The voice runtime remains owned by `cvsz/z-platform`:

```text
Browser / zDash /voice
  │ POST /api/voice/session with zDash JWT + tenant header
  ▼
zDash FastAPI voice broker
  │ server-side ZPLATFORM_VOICE_SERVICE_TOKEN
  ▼
z-platform voice-gateway :8450
  │ one-time signed ticket
  ▼
Browser WebSocket -> z-platform voice-gateway -> voice-agent
                                           └-> ai-gateway -> local LLM
```

The browser never receives the z-platform service token or provider credentials.

## Prerequisite

Deploy the voice stack from `cvsz/z-platform` PR `#144` or its merged successor. The required z-platform services are:

- `voice-gateway`
- `voice-agent`
- `ai-gateway`
- one supported LLM runtime: Ollama, llama.cpp, or vLLM

For local development, the expected gateway endpoints are:

```text
HTTP ticket API: http://127.0.0.1:8450/v1/voice/tickets
WebSocket:       ws://127.0.0.1:8450/v1/realtime
```

## zDash backend configuration

Copy the voice values from `.env.production.example` into the backend environment:

```env
ZPLATFORM_VOICE_ENABLED=true
ZPLATFORM_VOICE_GATEWAY_URL=http://127.0.0.1:8450
ZPLATFORM_VOICE_SERVICE_TOKEN=<same value as z-platform Z_PLATFORM_SERVICE_TOKEN>
ZPLATFORM_VOICE_MODEL=qwen3:8b
ZPLATFORM_VOICE_REQUEST_TIMEOUT_SECONDS=5
```

Never use a `VITE_` prefix for the service token. Vite-prefixed variables are compiled into browser assets.

## z-platform configuration

The z-platform voice gateway must expose a browser-reachable `VOICE_PUBLIC_WS_URL`:

```env
VOICE_PUBLIC_WS_URL=ws://127.0.0.1:8450/v1/realtime
```

For production:

```env
VOICE_PUBLIC_WS_URL=wss://voice.zeaz.dev/v1/realtime
VOICE_ALLOW_ANONYMOUS=false
```

Use TLS and the approved Cloudflare Access/OIDC boundary before exposing the WebSocket publicly.

## Container networking

When the zDash backend runs directly on the host, use:

```env
ZPLATFORM_VOICE_GATEWAY_URL=http://127.0.0.1:8450
```

When zDash runs in Docker and z-platform runs on the host:

```env
ZPLATFORM_VOICE_GATEWAY_URL=http://host.docker.internal:8450
```

On Linux Docker Engine, add the host gateway mapping if it is not already present:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

A production deployment should place both backends on an approved private network and use an internal DNS name rather than a published host port.

## API contract

### `GET /api/voice/status`

Returns the current zDash-side configuration state and configured model. It never returns the service token.

### `POST /api/voice/session`

Request:

```json
{
  "instructions": "You are a concise, helpful voice assistant."
}
```

zDash derives the subject from the authenticated JWT and the tenant from `X-ZDash-Tenant`. It calls the trusted z-platform ticket endpoint and returns:

```json
{
  "ok": true,
  "data": {
    "ticket": "<short-lived-signed-ticket>",
    "websocket_url": "wss://voice.zeaz.dev/v1/realtime",
    "expires_at": "2026-08-02T01:00:00Z",
    "ticket_transport": "sec-websocket-protocol",
    "model": "qwen3:8b",
    "instructions": "You are a concise, helpful voice assistant."
  },
  "error": null,
  "timestamp": "..."
}
```

The broker validates that the gateway returns a `ws://` or `wss://` URL and the expected ticket transport.

## Browser behavior

The native `/voice` page:

- captures microphone audio with an AudioWorklet;
- resamples to 16 kHz mono PCM16;
- sends OpenAI Realtime-compatible audio events;
- renders user and assistant transcripts;
- streams PCM response audio;
- clears queued playback on `speech_started` for barge-in;
- supports mute, response cancellation, and explicit session stop.

Transcript state remains browser-local and is cleared on reload.

## Validation

Backend:

```bash
cd backend
python -m pytest -q tests/test_zplatform_voice.py
python -m ruff check app/api/voice.py app/integrations/zplatform_voice.py tests/test_zplatform_voice.py
```

Frontend:

```bash
cd frontend
npm test -- RealtimeVoiceClient.test.ts
npm run build
```

End to end:

1. Start the z-platform voice Compose profile.
2. Enable the zDash backend integration.
3. Sign in to zDash.
4. Open `/voice`.
5. Verify microphone permission, transcription, audio playback, interruption, cancellation, ticket expiry, and reconnect behavior.

## Production gate

Do not mark the integration production-ready until all of the following pass:

- HTTPS/WSS and reviewed identity boundary;
- `VOICE_ALLOW_ANONYMOUS=false` on z-platform;
- distinct, secret-managed service and ticket signing keys;
- Redis-backed ticket replay protection before multiple voice-gateway replicas;
- load tests matched to STT/TTS/LLM hardware capacity;
- microphone consent, privacy notice, retention policy, and audit review;
- browser tests on Chrome, Edge, Safari, and the target mobile devices;
- human release approval.
