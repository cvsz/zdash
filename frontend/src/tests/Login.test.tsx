import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import LoginForm from "../components/auth/LoginForm";
import { useAuth } from "../hooks/useAuth";

vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("LoginForm", () => {
  it("shows warning for default admin credentials", () => {
    mockedUseAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      isAdmin: false,
      isDevBypass: false,
      mode: "token",
      login: vi.fn(),
      logout: vi.fn(),
      refreshProfile: vi.fn(),
    });

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Username / Email"), {
      target: { value: "admin" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "dev-only-change-before-production" },
    });

    expect(screen.getByText(/Default admin credentials detected/i)).toBeTruthy();
  });

  it("submits credentials through auth hook", async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    const onAuthenticated = vi.fn();

    mockedUseAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      isAdmin: false,
      isDevBypass: false,
      mode: "token",
      login,
      logout: vi.fn(),
      refreshProfile: vi.fn(),
    });

    render(<LoginForm onAuthenticated={onAuthenticated} />);

    fireEvent.change(screen.getByLabelText("Username / Email"), {
      target: { value: "operator@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "safe-password" },
    });

    fireEvent.submit(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("operator@example.com", "safe-password");
      expect(onAuthenticated).toHaveBeenCalled();
    });
  });
});
