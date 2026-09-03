import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createProject, updateProject } from "../api";
import type { Project } from "../types";
import ProjectForm from "./ProjectForm";

vi.mock("../api", () => ({ createProject: vi.fn(), updateProject: vi.fn() }));

const mockedCreateProject = vi.mocked(createProject);
const mockedUpdateProject = vi.mocked(updateProject);

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
    mockedUpdateProject.mockReset();
  });

  it("renders the project creation form", () => {
    render(
      <ProjectForm userId="hossein" editing={null} onSaved={() => {}} onCancelEdit={() => {}} />,
    );

    expect(screen.getByText("Create a project")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create project/i })).toBeEnabled();
  });

  it("submits a cleaned payload and resets the fields on success", async () => {
    mockedCreateProject.mockResolvedValueOnce(createdProject);
    const onSaved = vi.fn();
    render(
      <ProjectForm userId="hossein" editing={null} onSaved={onSaved} onCancelEdit={() => {}} />,
    );

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

  it("prefills fields in edit mode and submits an update", async () => {
    mockedUpdateProject.mockResolvedValueOnce(createdProject);
    const onSaved = vi.fn();
    const onCancelEdit = vi.fn();
    render(
      <ProjectForm
        userId="hossein"
        editing={createdProject}
        onSaved={onSaved}
        onCancelEdit={onCancelEdit}
      />,
    );

    expect(screen.getByText("Edit project")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("What is this project called?")).toHaveValue(
      "Calendar Sync",
    );
    expect(screen.getByPlaceholderText(/comma-separated/i)).toHaveValue("Python");

    fireEvent.change(screen.getByPlaceholderText("What will this project do?"), {
      target: { value: "Updated description." },
    });
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));

    await waitFor(() =>
      expect(mockedUpdateProject).toHaveBeenCalledWith(
        "calendar-sync",
        expect.objectContaining({ description: "Updated description." }),
      ),
    );
    expect(onCancelEdit).toHaveBeenCalled();
    expect(onSaved).toHaveBeenCalled();
  });

  it("shows an error message when the API call fails", async () => {
    mockedCreateProject.mockRejectedValueOnce(new Error("Validation Error"));
    render(
      <ProjectForm userId="hossein" editing={null} onSaved={() => {}} onCancelEdit={() => {}} />,
    );

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
