import { act, waitFor } from "@testing-library/react";

export async function flushPromises() {
  await act(async () => {
    await new Promise<void>((resolve) => {
      setTimeout(resolve, 0);
    });
  });
}

export async function waitForStableUi() {
  await flushPromises();
  await waitFor(() => {
    expect(document.body).toBeTruthy();
  });
}
