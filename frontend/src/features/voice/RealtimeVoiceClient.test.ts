import { describe, expect, it } from "vitest";

import { pcm16ToFloat32, resampleToPcm16 } from "./RealtimeVoiceClient";

describe("voice audio conversion", () => {
  it("resamples float audio to bounded PCM16", () => {
    const input = new Float32Array([1.5, 1, 0.5, 0, -0.5, -1, -1.5, 0]);
    const pcm = resampleToPcm16(input, 16_000, 16_000);
    expect(pcm.byteLength).toBe(input.length * 2);

    const view = new DataView(pcm.buffer, pcm.byteOffset, pcm.byteLength);
    expect(view.getInt16(0, true)).toBe(32767);
    expect(view.getInt16(10, true)).toBe(-32768);
  });

  it("converts PCM16 frames back to normalized float samples", () => {
    const buffer = new ArrayBuffer(6);
    const view = new DataView(buffer);
    view.setInt16(0, 32767, true);
    view.setInt16(2, 0, true);
    view.setInt16(4, -32768, true);

    const samples = pcm16ToFloat32(new Uint8Array(buffer));
    expect(samples[0]).toBeCloseTo(1, 4);
    expect(samples[1]).toBe(0);
    expect(samples[2]).toBe(-1);
  });

  it("returns an empty frame for invalid input", () => {
    expect(resampleToPcm16(new Float32Array(), 48_000)).toHaveLength(0);
    expect(resampleToPcm16(new Float32Array([0.1]), 0)).toHaveLength(0);
  });
});
