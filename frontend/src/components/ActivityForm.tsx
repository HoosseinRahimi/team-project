import { useEffect, useState } from "react";

import { createActivity, updateActivity } from "../api";
import type { Activity, ActivityInput, ActivityStatus, Project } from "../types";

interface Props {
  userId: string;
  projects: Project[];
  editing: Activity | null;
  onSaved: () => Promise<void> | void;
  onCancelEdit: () => void;
}

const today = new Date().toISOString().slice(0, 10);

export default function ActivityForm({ userId, projects, editing, onSaved, onCancelEdit }: Props) {
  const [date, setDate] = useState(today);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState<ActivityStatus>("planned");
  const [projectId, setProjectId] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (editing) {
      setDate(editing.date);
      setTitle(editing.title);
      setStatus(editing.status);
      setProjectId(editing.projectId ?? "");
    } else {
      setDate(today);
      setTitle("");
      setStatus("planned");
      setProjectId("");
    }
    setError("");
  }, [editing]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const payload: ActivityInput = {
      userId,
      date,
      title: title.trim(),
      status,
      projectId: projectId || null,
    };
    try {
      if (editing) await updateActivity(editing.id, payload);
      else await createActivity(payload);
      setTitle("");
      setStatus("planned");
      setProjectId("");
      onCancelEdit();
      await onSaved();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not save activity.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="activity-form" onSubmit={submit}>
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">Activity system</p>
          <h2>{editing ? "Edit activity" : "Add activity"}</h2>
        </div>
      </div>
      <div className="form-grid">
        <label>
          Date
          <input
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            required
          />
        </label>
        <label>
          Status
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as ActivityStatus)}
          >
            <option value="planned">Planned</option>
            <option value="in-progress">In progress</option>
            <option value="completed">Completed</option>
          </select>
        </label>
        <label className="form-span-2">
          Title
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="What are you working on?"
            maxLength={200}
            required
          />
        </label>
        <label className="form-span-2">
          Project
          <select value={projectId} onChange={(event) => setProjectId(event.target.value)}>
            <option value="">No project</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      {error ? <p className="form-error">{error}</p> : null}
      <div className="form-actions">
        <button className="primary-button" type="submit" disabled={saving}>
          {saving ? "Saving…" : editing ? "Save changes" : "Add activity"}
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
