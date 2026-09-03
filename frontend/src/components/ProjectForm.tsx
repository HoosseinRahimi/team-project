import { useEffect, useState } from "react";

import { createProject, updateProject } from "../api";
import type { Project, ProjectInput, ProjectStatus } from "../types";

interface Props {
  userId: string;
  editing: Project | null;
  onSaved: () => Promise<void> | void;
  onCancelEdit: () => void;
}

export default function ProjectForm({ userId, editing, onSaved, onCancelEdit }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [technology, setTechnology] = useState("");
  const [status, setStatus] = useState<ProjectStatus>("planned");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (editing) {
      setName(editing.name);
      setDescription(editing.description);
      setTechnology(editing.technology.join(", "));
      setStatus(editing.status as ProjectStatus);
    } else {
      setName("");
      setDescription("");
      setTechnology("");
      setStatus("planned");
    }
    setError("");
  }, [editing]);

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
      if (editing) await updateProject(editing.id, payload);
      else await createProject(payload);
      setName("");
      setDescription("");
      setTechnology("");
      setStatus("planned");
      onCancelEdit();
      await onSaved();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not save project.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="project-form" onSubmit={submit}>
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">Project workspace</p>
          <h2>{editing ? "Edit project" : "Create a project"}</h2>
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
          {saving ? "Saving…" : editing ? "Save changes" : "Create project"}
        </button>
        {editing ? (
          <button className="secondary-button" type="button" onClick={onCancelEdit}>
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
