import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ContentPipeline from "../pages/ContentPipeline";

describe("ContentPipeline", () => {
  it("renders content board, policy notes, and dry-run safety indicators", async () => {
    render(<ContentPipeline />);

    expect(screen.getByRole("heading", { name: "Content Pipeline", level: 2 })).toBeTruthy();
    expect(screen.getByText("SOCIAL_DRY_RUN")).toBeTruthy();
    expect(screen.getByText("Approval Required")).toBeTruthy();
    expect(screen.getByText("Content Board")).toBeTruthy();
    const policyNotes = await screen.findAllByText(/Policy notes/i);
    expect(policyNotes.length).toBeGreaterThan(0);
  });

  it("keeps publish action disabled until approved", async () => {
    render(<ContentPipeline />);

    const publishButtons = (await screen.findAllByText(
      "Dry-run publish",
    )) as HTMLButtonElement[];
    expect(publishButtons.length).toBeGreaterThan(0);
    expect(publishButtons[0].disabled).toBe(true);
  });
});
