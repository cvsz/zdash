import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  applyStoredSession,
  clearStoredSession,
  getCurrentUser,
  loginWithPassword,
  logoutSession,
  readStoredSession,
  refreshSession,
} from "../api/auth";
import { setUnauthorizedHandler } from "../api/client";
import { ApiError, type AuthUser, type StoredAuthSession } from "../api/types";

type AuthMode = "anonymous" | "token" | "dev";
const frontendAuthEnabled =
  String(import.meta.env.VITE_AUTH_ENABLED ?? "false").toLowerCase() === "true";
const devUser: AuthUser = { username: "dev-user", role: "admin" };

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isDevBypass: boolean;
  mode: AuthMode;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function clearAuthState(
  setStored: (session: StoredAuthSession | null) => void,
  setUser: (user: AuthUser | null) => void,
  setMode: (mode: AuthMode) => void,
) {
  clearStoredSession();
  applyStoredSession(null);
  setStored(null);
  setUser(null);
  setMode("anonymous");
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() =>
    frontendAuthEnabled ? null : devUser,
  );
  const [loading, setLoading] = useState(frontendAuthEnabled);
  const [mode, setMode] = useState<AuthMode>(
    frontendAuthEnabled ? "anonymous" : "dev",
  );
  const [storedSession, setStoredSession] = useState<StoredAuthSession | null>(() =>
    readStoredSession(),
  );

  const refreshProfile = useCallback(async () => {
    const nextStored = readStoredSession();
    setStoredSession(nextStored);
    applyStoredSession(nextStored);

    try {
      const me = await getCurrentUser();
      setUser(me);
      setMode(nextStored ? "token" : "dev");
      return;
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.status === 401 &&
        nextStored?.refreshToken
      ) {
        try {
          await refreshSession(nextStored.refreshToken);
          const rotatedStored = readStoredSession();
          setStoredSession(rotatedStored);
          applyStoredSession(rotatedStored);
          const me = await getCurrentUser();
          setUser(me);
          setMode("token");
          return;
        } catch {
          // falls through to clear state
        }
      }
      clearAuthState(setStoredSession, setUser, setMode);
    }
  }, []);

  useEffect(() => {
    let active = true;

    const bootstrap = async () => {
      if (!frontendAuthEnabled) {
        return;
      }
      setLoading(true);
      await refreshProfile();
      if (active) {
        setLoading(false);
      }
    };

    void bootstrap();
    return () => {
      active = false;
    };
  }, [refreshProfile]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearAuthState(setStoredSession, setUser, setMode);
    });
    return () => {
      setUnauthorizedHandler(undefined);
    };
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      if (!frontendAuthEnabled) {
        setUser(devUser);
        setMode("dev");
        return;
      }
      setLoading(true);
      try {
        await loginWithPassword(username, password);
        await refreshProfile();
      } finally {
        setLoading(false);
      }
    },
    [refreshProfile],
  );

  const logout = useCallback(async () => {
    if (!frontendAuthEnabled) {
      setUser(devUser);
      setMode("dev");
      return;
    }
    setLoading(true);
    try {
      await logoutSession(storedSession?.refreshToken);
    } finally {
      clearAuthState(setStoredSession, setUser, setMode);
      setLoading(false);
    }
  }, [storedSession?.refreshToken]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role === "admin",
      isDevBypass: mode === "dev",
      mode,
      login,
      logout,
      refreshProfile,
    }),
    [loading, login, logout, mode, refreshProfile, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
