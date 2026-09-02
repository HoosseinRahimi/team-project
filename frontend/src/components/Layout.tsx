import type { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" data-link>
          Team Project
        </a>
        <span className="header-label">Local workspace</span>
      </header>
      <main className="page-content">{children}</main>
    </div>
  );
}
