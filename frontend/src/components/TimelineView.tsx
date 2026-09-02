import type { Activity } from "../types";

interface Props {
  activities: Activity[];
  onEdit: (activity: Activity) => void;
  onDelete: (activity: Activity) => void;
}

export default function TimelineView({ activities, onEdit, onDelete }: Props) {
  const groups = new Map<string, Activity[]>();
  for (const activity of [...activities].sort((a, b) => b.date.localeCompare(a.date))) {
    const group = groups.get(activity.date) ?? [];
    group.push(activity);
    groups.set(activity.date, group);
  }

  return (
    <section className="dashboard-card timeline-card">
      <div className="section-heading compact">
        <div>
          <p className="eyebrow">Timeline</p>
          <h2>Work history</h2>
        </div>
        <span className="member-count">{activities.length}</span>
      </div>
      {groups.size === 0 ? <p className="status-message">No activities recorded yet.</p> : null}
      <div className="timeline-list">
        {[...groups.entries()].map(([date, items]) => (
          <section className="timeline-group" key={date}>
            <time>{date}</time>
            <div>
              {items.map((activity) => (
                <article className="timeline-item" key={activity.id}>
                  <span className={`status-dot ${activity.status}`} />
                  <div className="timeline-copy">
                    <h3>{activity.title}</h3>
                    <span className={`pill ${activity.status}`}>{activity.status}</span>
                  </div>
                  <div className="item-actions">
                    <button type="button" onClick={() => onEdit(activity)}>
                      Edit
                    </button>
                    <button type="button" onClick={() => onDelete(activity)}>
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}
