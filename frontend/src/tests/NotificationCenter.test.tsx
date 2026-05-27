import { render, screen } from "@testing-library/react";
import NotificationCenter from "../components/system/NotificationCenter";
import { RealtimeContext } from "../realtime/context";

test("renders notification center button", () => {
  render(
    <RealtimeContext.Provider value={{ state: "connected", events: [], unread: 0, clearUnread: () => {} }}>
      <NotificationCenter />
    </RealtimeContext.Provider>,
  );
  expect(screen.getByLabelText("Notifications")).toBeInTheDocument();
});
