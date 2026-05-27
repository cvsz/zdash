import { render } from "@testing-library/react";
import ErrorBoundary from "../components/system/ErrorBoundary";

test("error boundary renders children for realtime-safe path", () => {
  const { getByText } = render(<ErrorBoundary><div>ok</div></ErrorBoundary>);
  expect(getByText("ok")).toBeInTheDocument();
});
