import type { User } from "../types";

export default function MemberList({ users }: { users: User[] }) {
  return (
    <div className="member-grid">
      {users.map((user) => (
        <a className="member-card" href={`/users/${user.id}`} data-link key={user.id}>
          <span className="member-avatar">{user.name.charAt(0)}</span>
          <span>
            <strong>{user.name}</strong>
            <small>{user.role}</small>
          </span>
          <span className="card-arrow" aria-hidden="true">
            →
          </span>
        </a>
      ))}
    </div>
  );
}
