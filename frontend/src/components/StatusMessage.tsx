import type { ReactNode } from "react";

export default function StatusMessage({
  children,
  error = false,
}: {
  children: ReactNode;
  error?: boolean;
}) {
  return <p className={error ? "status-message error" : "status-message"}>{children}</p>;
}
