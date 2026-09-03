import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createProject } from "../api";
import type { Project } from "../types";
import ProjectForm from "./ProjectForm";

vi.mock("../api", () => ({ createProject: vi.fn() }));

const mockedCreateProject = vi.mocked(createProject);

const createdProject: Project = {
  id: "calendar-sync",
  userId: "hossein",
  name: "Calendar Sync",
  description: "Keep calendar entries in sync.",
  technology: ["Python"],
  status: "planned",
};

describe("ProjectForm", () => {
  beforeEach(() => {
    mockedCreateProject.mockReset();
  });

  it("renders the project creation form", () => {
    render(<ProjectForm userId="hossein" onSaved={() => {}} />);

    expect(screen.getByText("Create a project")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create project/i })).toBeEnabled();
  });

  it("submits a cleaned payload and resets the fields on success", async () => {
    mockedCreateProject.mockResolvedValueOnce(createdProject);
    const onSaved = vi.fn();
    render(<ProjectForm userId="hossein" onSaved={onSaved} />);

    fireEvent.change(screen.getByPlaceholderText("What is this project called?"), {
      target: { value: "  Calendar Sync  " },
    });
    fireEvent.change(screen.getByPlaceholderText("What will this project do?"), {
      target: { value: "Keep calendar entries in sync." },
    });
    fireEvent.change(screen.getByPlaceholderText(/comma-separated/i), {
      target: { value: " Python, React , " },
    });
    fireEvent.click(screen.getByRole("button", { name: /create project/i }));

    await waitFor(() =>
      expect(mockedCreateProject).toHaveBeenCalledWith({
        userId: "hossein",
        name: "Calendar Sync",
        description: "Keep calendar entries in sync.",
        technology: ["Python", "React"],
        status: "planned",
      }),
    );
    expect(onSaved).toHaveBeenCalled();
    expect(screen.getByPlaceholderText("What is this project called?")).toHaveValue("");
  });

  it("shows an error message when the API call fails", async () => {
    mockedCreateProject.mockRejectedValueOnce(new Error("Validation Error"));
    render(<ProjectForm userId="hossein" onSaved={() => {}} />);

    fireEvent.change(screen.getByPlaceholderText("What is this project called?"), {
      target: { value: "Broken Project" },
    });
    fireEvent.change(screen.getByPlaceholderText("What will this project do?"), {
      target: { value: "This submission fails." },
    });
    fireEvent.click(screen.getByRole("button", { name: /create project/i }));

    expect(await screen.findByText("Validation Error")).toBeInTheDocument();
  });
});
