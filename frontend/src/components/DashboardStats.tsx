import type { Activity, Project } from "../types";

export default function DashboardStats({
  activities,
  projects,
}: {
  activities: Activity[];
  projects: Project[];
}) {
  const completed = activities.filter((activity) => activity.status === "completed").length;
  const inProgress = activities.filter((activity) => activity.status === "in-progress").length;
  const activeProjects = projects.filter((project) => project.status === "active").length;

  return (
    <div className="stats-grid">
      <article className="stat-card">
        <span>Total activities</span>
        <strong>{activities.length}</strong>
      </article>
      <article className="stat-card">
        <span>Completed</span>
        <strong>{completed}</strong>
      </article>
      <article className="stat-card">
        <span>In progress</span>
        <strong>{inProgress}</strong>
      </article>
      <article className="stat-card">
        <span>Active projects</span>
        <strong>{activeProjects}</strong>
      </article>
    </div>
  );
}
