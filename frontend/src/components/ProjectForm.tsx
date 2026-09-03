import { useState } from "react";

import { createProject } from "../api";
import type { ProjectInput, ProjectStatus } from "../types";

interface Props {
  userId: string;
  onSaved: () => Promise<void> | void;
}

export default function ProjectForm({ userId, onSaved }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [technology, setTechnology] = useState("");
  const [status, setStatus] = useState<ProjectStatus>("planned");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const payload: ProjectInput = {
      userId,
      name: name.trim(),
      description: description.trim(),
      technology: technology
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      status,
    };
    try {
      await createProject(payload);
      setName("");
      setDescription("");
      setTechnology("");
      setStatus("planned");
      await onSaved();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not create project.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="project-form" onSubmit={submit}>
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">Project workspace</p>
          <h2>Create a project</h2>
        </div>
      </div>
      <div className="form-grid">
        <label className="form-span-2">
          Name
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="What is this project called?"
            maxLength={120}
            required
          />
        </label>
        <label className="form-span-2">
          Description
          <input
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="What will this project do?"
            maxLength={500}
            required
          />
        </label>
        <label>
          Technology
          <input
            value={technology}
            onChange={(event) => setTechnology(event.target.value)}
            placeholder="Comma-separated, e.g. Python, React"
          />
        </label>
        <label>
          Status
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as ProjectStatus)}
          >
            <option value="planned">Planned</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </label>
      </div>
      {error ? <p className="form-error">{error}</p> : null}
      <div className="form-actions">
        <button className="primary-button" type="submit" disabled={saving}>
          {saving ? "Creating…" : "Create project"}
        </button>
      </div>
    </form>
  );
}
