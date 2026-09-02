import { useEffect, useState } from "react";

import { deleteActivity, getActivities, getProjects, getUsers } from "./api";
import ActivityForm from "./components/ActivityForm";
import CalendarView from "./components/CalendarView";
import DashboardStats from "./components/DashboardStats";
import Layout from "./components/Layout";
import MemberList from "./components/MemberList";
import StatusMessage from "./components/StatusMessage";
import TimelineView from "./components/TimelineView";
import type { Activity, Project, User } from "./types";

function usePathname(): string {
  const [pathname, setPathname] = useState(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => setPathname(window.location.pathname);
    const handleLinkClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      const link = target?.closest<HTMLAnchorElement>("a[data-link]");
      if (!link || link.origin !== window.location.origin) return;
      event.preventDefault();
      window.history.pushState({}, "", link.pathname);
      setPathname(link.pathname);
    };

    window.addEventListener("popstate", handlePopState);
    document.addEventListener("click", handleLinkClick);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      document.removeEventListener("click", handleLinkClick);
    };
  }, []);

  return pathname;
}

function LandingPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getUsers()
      .then(setUsers)
      .catch((requestError: Error) => setError(requestError.message));
  }, []);

  return (
    <section className="landing-page">
      <div className="hero">
        <p className="eyebrow">University team workspace</p>
        <h1>
          Build together.
          <br />
          <em>Track progress.</em>
        </h1>
        <p className="hero-copy">
          A shared home for the team&apos;s daily work, personal projects, and next steps.
        </p>
      </div>
      <div className="section-heading">
        <div>
          <p className="eyebrow">The team</p>
          <h2>Meet the members</h2>
        </div>
        <span className="member-count">{users.length.toString().padStart(2, "0")} members</span>
      </div>
      {error ? <StatusMessage error>{error}</StatusMessage> : null}
      {!error && users.length === 0 ? <StatusMessage>Loading team members…</StatusMessage> : null}
      {users.length > 0 ? <MemberList users={users} /> : null}
    </section>
  );
}

interface TeamState {
  users: User[];
  activities: Activity[];
  projects: Project[];
}

function UserPage({ userId }: { userId: string }) {
  const [state, setState] = useState<TeamState>({ users: [], activities: [], projects: [] });
  const [error, setError] = useState("");
  const [editing, setEditing] = useState<Activity | null>(null);

  async function loadData() {
    const [users, activities, projects] = await Promise.all([
      getUsers(),
      getActivities(),
      getProjects(),
    ]);
    setState({ users, activities, projects });
  }

  useEffect(() => {
    loadData().catch((requestError: Error) => setError(requestError.message));
  }, []);

  const user = state.users.find((candidate) => candidate.id === userId);
  const activities = state.activities.filter((activity) => activity.userId === userId);
  const projects = state.projects.filter((project) => project.userId === userId);

  async function removeActivity(activity: Activity) {
    if (!window.confirm(`Delete "${activity.title}"?`)) return;
    try {
      await deleteActivity(activity.id);
      if (editing?.id === activity.id) setEditing(null);
      await loadData();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Could not delete activity.");
    }
  }

  if (error) return <StatusMessage error>{error}</StatusMessage>;
  if (state.users.length === 0) return <StatusMessage>Loading user dashboard…</StatusMessage>;
  if (!user) {
    return (
      <div className="empty-state">
        <p className="eyebrow">404</p>
        <h1>User not found</h1>
        <a className="text-link" href="/" data-link>
          Back to the team
        </a>
      </div>
    );
  }

  return (
    <section className="user-page">
      <a className="back-link" href="/" data-link>
        ← All members
      </a>
      <div className="profile-header dashboard-profile">
        <span className="profile-avatar">{user.name.charAt(0)}</span>
        <div>
          <p className="eyebrow">Member dashboard</p>
          <h1>{user.name}</h1>
          <p className="role-label">{user.role}</p>
        </div>
      </div>

      <DashboardStats activities={activities} projects={projects} />

      <div className="dashboard-grid">
        <ActivityForm
          userId={userId}
          projects={projects}
          editing={editing}
          onSaved={loadData}
          onCancelEdit={() => setEditing(null)}
        />
        <CalendarView activities={activities} />
      </div>

      <TimelineView activities={activities} onEdit={setEditing} onDelete={removeActivity} />

      <section className="dashboard-card projects-card">
        <div className="section-heading compact">
          <div>
            <p className="eyebrow">Projects</p>
            <h2>Connected work</h2>
          </div>
          <span className="member-count">{projects.length}</span>
        </div>
        {projects.length > 0 ? (
          <div className="project-list">
            {projects.map((project) => (
              <article className="project-item" key={project.id}>
                <span className="project-mark">↗</span>
                <div>
                  <h3>{project.name}</h3>
                  <p>{project.description}</p>
                  <small>{project.technology.join(" · ") || "No technology listed"}</small>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <StatusMessage>No projects recorded yet.</StatusMessage>
        )}
      </section>
    </section>
  );
}

export default function App() {
  const pathname = usePathname();
  const userMatch = pathname.match(/^\/users\/([^/]+)\/?$/);

  return (
    <Layout>
      {pathname === "/" ? (
        <LandingPage />
      ) : userMatch ? (
        <UserPage userId={userMatch[1]} />
      ) : (
        <div className="empty-state">
          <p className="eyebrow">404</p>
          <h1>Page not found</h1>
          <a className="text-link" href="/" data-link>
            Back home
          </a>
        </div>
      )}
    </Layout>
  );
}
