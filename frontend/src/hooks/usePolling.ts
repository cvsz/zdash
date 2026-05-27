import { useEffect, useRef, useState } from "react";

type UsePollingResult = {
  active: boolean;
  pause: () => void;
  resume: () => void;
  runNow: () => void;
};

export function usePolling(callback: () => void, intervalMs = 5000): UsePollingResult {
  const [active, setActive] = useState(true);
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    if (!active || intervalMs <= 0) {
      return undefined;
    }

    const id = window.setInterval(() => {
      callbackRef.current();
    }, intervalMs);

    return () => {
      window.clearInterval(id);
    };
  }, [active, intervalMs]);

  return {
    active,
    pause: () => setActive(false),
    resume: () => setActive(true),
    runNow: () => callbackRef.current(),
  };
}
