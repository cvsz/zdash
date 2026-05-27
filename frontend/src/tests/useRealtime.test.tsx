import { renderHook } from "@testing-library/react";
import { useRealtime } from "../realtime/useRealtime";

test("useRealtime returns stable object", () => {
  const { result } = renderHook(() => useRealtime());
  expect(result.current.connection).toBeTruthy();
});
