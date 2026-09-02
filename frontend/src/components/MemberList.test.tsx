import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MemberList from "./MemberList";
import type { User } from "../types";

const users: User[] = [
  { id: "hossein", name: "Hossein", role: "Developer" },
  { id: "ali", name: "Ali", role: "Developer" },
];

describe("MemberList", () => {
  it("renders a link to each member page", () => {
    render(<MemberList users={users} />);

    for (const user of users) {
      const link = screen.getByRole("link", { name: new RegExp(user.name) });
      expect(link).toHaveAttribute("href", `/users/${user.id}`);
    }
  });
});
