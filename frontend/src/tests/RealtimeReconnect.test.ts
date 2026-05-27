import { describe, expect, it, vi } from "vitest";

import { computeReconnectDelay } from "../realtime/reconnect";

describe("computeReconnectDelay", () => {
  it("grows exponentially and is capped", () => {
    const randomSpy = vi.spyOn(Math, "random").mockReturnValue(0);

    const a0 = computeReconnectDelay(0, { baseDelayMs: 500, maxDelayMs: 4000, jitterRatio: 0.2 });
    const a1 = computeReconnectDelay(1, { baseDelayMs: 500, maxDelayMs: 4000, jitterRatio: 0.2 });
    const a2 = computeReconnectDelay(2, { baseDelayMs: 500, maxDelayMs: 4000, jitterRatio: 0.2 });
    const a6 = computeReconnectDelay(6, { baseDelayMs: 500, maxDelayMs: 4000, jitterRatio: 0.2 });

    expect(a0).toBe(500);
    expect(a1).toBe(1000);
    expect(a2).toBe(2000);
    expect(a6).toBe(4000);

    randomSpy.mockRestore();
  });
});
