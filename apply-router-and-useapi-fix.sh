#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "zDash frontend router/useApi repair"
echo "=================================================="

FRONTEND_DIR="$HOME/zdash/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "[ERROR] frontend directory not found: $FRONTEND_DIR"
  exit 1
fi

cd "$FRONTEND_DIR"

echo
echo "[1/5] Patching src/hooks/useApi.ts"

cat > src/hooks/useApi.ts <<'TS'
import {
  DependencyList,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: DependencyList = [],
): ApiState<T> {
  const mountedRef = useRef(true);

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async () => {
    try {
      if (mountedRef.current) {
        setLoading(true);
      }

      const result = await fetcher();

      if (!mountedRef.current) {
        return;
      }

      setData(result);
      setError(null);
    } catch (err) {
      if (!mountedRef.current) {
        return;
      }

      const message =
        err instanceof Error ? err.message : 'Unknown API error';

      setError(message);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, deps);

  useEffect(() => {
    mountedRef.current = true;

    void run();

    return () => {
      mountedRef.current = false;
    };
  }, [run]);

  return {
    data,
    loading,
    error,
    refetch: run,
  };
}
TS

echo
echo "[2/5] Patching BrowserRouter future flags"

python3 <<'PY'
from pathlib import Path
import re

path = Path("src/App.tsx")

if path.exists():
    s = path.read_text()

    if "v7_startTransition" not in s:
        s = re.sub(
            r"<BrowserRouter>",
            """<BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >""",
            s,
        )

    path.write_text(s)
    print("Patched App.tsx")
else:
    print("Skipped App.tsx (not found)")
PY

echo
echo "[3/5] Patching MemoryRouter future flags"

python3 <<'PY'
from pathlib import Path
import re

path = Path("src/tests/ProtectedRoute.test.tsx")

if path.exists():
    s = path.read_text()

    s = re.sub(
        r'<MemoryRouter initialEntries=\{\["([^"]+)"\]\}>',
        r'''<MemoryRouter
        initialEntries={["\1"]}
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >''',
        s,
    )

    path.write_text(s)
    print("Patched ProtectedRoute.test.tsx")
else:
    print("Skipped ProtectedRoute.test.tsx (not found)")
PY

echo
echo "[4/5] Running frontend validation"

source ~/.nvm/nvm.sh
nvm use 20 >/dev/null

npm test
npm run build

echo
echo "[5/5] Done"

echo
echo "=================================================="
echo "Patch applied successfully"
echo "=================================================="
