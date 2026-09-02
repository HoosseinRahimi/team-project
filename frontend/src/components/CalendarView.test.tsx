import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Activity } from "../types";
import CalendarView from "./CalendarView";

const activities: Activity[] = [
  {
    id: "hossein-2026-09-02-review",
    userId: "hossein",
    date: "2026-09-02",
    title: "Review pull requests",
    status: "planned",
    projectId: null,
  },
];

describe("CalendarView", () => {
  it("shows activities for a selected date", () => {
    render(<CalendarView activities={activities} />);

    fireEvent.click(screen.getByRole("button", { name: "2026-09-02, 1 activity" }));
    expect(screen.getByText("Review pull requests")).toBeInTheDocument();
  });
});
