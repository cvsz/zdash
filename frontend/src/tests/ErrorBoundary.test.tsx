import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ErrorBoundary from "../components/system/ErrorBoundary";

function Broken() {
  throw new Error("fail");
}

function preventExpectedBoundaryError(event: ErrorEvent) {
  if (event.error instanceof Error && event.error.message === "fail") {
    event.preventDefault();
  }
}

describe("ErrorBoundary", () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    window.addEventListener("error", preventExpectedBoundaryError);

    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation((...args) => {
      const message = args.map((arg) => String(arg)).join(" ");

      if (
        message.includes("Error: fail") ||
        message.includes("Error: Uncaught") ||
        message.includes("The above error occurred in the <Broken> component") ||
        message.includes("Dashboard runtime error boundary caught an error")
      ) {
        return;
      }
    });
  });

  afterEach(() => {
    window.removeEventListener("error", preventExpectedBoundaryError);
    consoleErrorSpy.mockRestore();
  });

  it("renders fallback UI when child throws", () => {
    render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText(/unexpected error/i)).toBeInTheDocument();
  });
});
