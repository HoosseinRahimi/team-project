import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ChessGame from "./ChessGame";

function square(name: string) {
  return screen.getByRole("button", { name: new RegExp(`^${name},`) });
}

describe("ChessGame", () => {
  it("renders the full board with white to move", () => {
    const { container } = render(<ChessGame />);
    expect(container.querySelectorAll(".chess-square")).toHaveLength(64);
    expect(screen.getByText(/White to move/)).toBeInTheDocument();
  });

  it("plays a move, shows it in the history, and flips the turn", () => {
    render(<ChessGame />);
    fireEvent.click(screen.getByRole("button", { name: "Two players" }));

    fireEvent.click(square("e2"));
    fireEvent.click(square("e4"));

    expect(screen.getByText(/Black to move/)).toBeInTheDocument();
    expect(screen.getByText(/1\. e4/)).toBeInTheDocument();
  });

  it("undoes the last move", () => {
    render(<ChessGame />);
    fireEvent.click(screen.getByRole("button", { name: "Two players" }));

    fireEvent.click(square("e2"));
    fireEvent.click(square("e4"));
    fireEvent.click(screen.getByRole("button", { name: "Undo" }));

    expect(screen.getByText(/White to move/)).toBeInTheDocument();
    expect(screen.queryByText(/1\. e4/)).not.toBeInTheDocument();
  });

  it("starts a fresh game on reset", () => {
    render(<ChessGame />);
    fireEvent.click(screen.getByRole("button", { name: "Two players" }));

    fireEvent.click(square("e2"));
    fireEvent.click(square("e4"));
    fireEvent.click(screen.getByRole("button", { name: "New game" }));

    expect(screen.getByText(/White to move/)).toBeInTheDocument();
    expect(square("e2")).toHaveTextContent("\u265F");
  });
});
