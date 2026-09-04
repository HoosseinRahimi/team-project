import { describe, expect, it } from "vitest";

import {
  applyMove,
  chooseComputerMove,
  createInitialState,
  getStatus,
  legalMoves,
  moveToSan,
  squareIndex,
  squareName,
  type ChessState,
  type Move,
  type Piece,
} from "./engine";

function findMove(state: ChessState, from: string, to: string, promotion?: string): Move {
  const candidates = legalMoves(state).filter(
    (move) => squareName(move.from) === from && squareName(move.to) === to,
  );
  expect(candidates.length, `move ${from}-${to}`).toBeGreaterThan(0);
  if (promotion) {
    const promoted = candidates.find((move) => move.promotion === promotion);
    expect(promoted, `promotion ${from}-${to}=${promotion}`).toBeDefined();
    return promoted as Move;
  }
  return candidates[0];
}

function playMoves(state: ChessState, ...pairs: string[][]): ChessState {
  let next = state;
  for (const [from, to, promotion] of pairs) {
    next = applyMove(next, findMove(next, from, to, promotion));
  }
  return next;
}

describe("chess engine", () => {
  it("maps square indices to algebraic names", () => {
    expect(squareName(0)).toBe("a8");
    expect(squareName(63)).toBe("h1");
    expect(squareName(squareIndex("e2"))).toBe("e2");
    expect(squareIndex("e4")).toBe(36);
  });

  it("offers 20 legal moves from the initial position", () => {
    expect(legalMoves(createInitialState())).toHaveLength(20);
  });

  it("sets the en passant target after a double pawn push", () => {
    const state = playMoves(createInitialState(), ["e2", "e4"]);
    expect(state.enPassantTarget).toBe(squareIndex("e3"));
  });

  it("captures en passant and removes the passed pawn", () => {
    const state = playMoves(
      createInitialState(),
      ["e2", "e4"],
      ["a7", "a6"],
      ["e4", "e5"],
      ["d7", "d5"],
    );
    expect(state.board[squareIndex("d5")]?.type).toBe("pawn");

    const captured = playMoves(state, ["e5", "d6"]);
    expect(captured.board[squareIndex("d5")]).toBeNull();
    expect(captured.board[squareIndex("d6")]?.type).toBe("pawn");
  });

  it("castles kingside and moves the rook", () => {
    const state = playMoves(
      createInitialState(),
      ["e2", "e4"],
      ["e7", "e5"],
      ["g1", "f3"],
      ["b8", "c6"],
      ["f1", "c4"],
      ["f8", "c5"],
    );
    const castling = legalMoves(state).find((move) => move.castle === "king");
    expect(castling).toBeDefined();

    const castled = applyMove(state, castling as Move);
    expect(castled.board[squareIndex("g1")]?.type).toBe("king");
    expect(castled.board[squareIndex("f1")]?.type).toBe("rook");
    expect(castled.board[squareIndex("e1")]).toBeNull();
    expect(castled.castling.whiteKingSide).toBe(false);
  });

  it("detects fool's mate as checkmate", () => {
    const before = playMoves(createInitialState(), ["f2", "f3"], ["e7", "e5"], ["g2", "g4"]);
    const queenMove = findMove(before, "d8", "h4");
    const state = applyMove(before, queenMove);

    const status = getStatus(state);
    expect(status.result).toBe("checkmate");
    expect(status.winner).toBe("black");
    expect(moveToSan(before, queenMove)).toBe("Qh4#");
  });

  it("detects stalemate", () => {
    const board: (Piece | null)[] = Array.from({ length: 64 }, () => null);
    board[squareIndex("h8")] = { type: "king", color: "black" };
    board[squareIndex("f7")] = { type: "queen", color: "white" };
    board[squareIndex("g6")] = { type: "king", color: "white" };
    const state: ChessState = {
      board,
      turn: "black",
      castling: {
        whiteKingSide: false,
        whiteQueenSide: false,
        blackKingSide: false,
        blackQueenSide: false,
      },
      enPassantTarget: null,
      fullmove: 1,
    };
    expect(getStatus(state)).toEqual({ inCheck: false, result: "stalemate", winner: null });
  });

  it("promotes a pawn and offers all four choices", () => {
    const board: (Piece | null)[] = Array.from({ length: 64 }, () => null);
    board[squareIndex("e7")] = { type: "pawn", color: "white" };
    board[squareIndex("a1")] = { type: "king", color: "white" };
    board[squareIndex("h8")] = { type: "king", color: "black" };
    const state: ChessState = {
      board,
      turn: "white",
      castling: {
        whiteKingSide: false,
        whiteQueenSide: false,
        blackKingSide: false,
        blackQueenSide: false,
      },
      enPassantTarget: null,
      fullmove: 1,
    };

    const promotions = legalMoves(state).filter((move) => move.from === squareIndex("e7"));
    expect(promotions).toHaveLength(4);

    const promoted = applyMove(state, findMove(state, "e7", "e8", "queen"));
    expect(promoted.board[squareIndex("e8")]?.type).toBe("queen");
    expect(promoted.board[squareIndex("e8")]?.color).toBe("white");
  });

  it("computer picks a legal move", () => {
    const initial = createInitialState();
    const move = chooseComputerMove(initial, 2);
    expect(move).not.toBeNull();
    expect(legalMoves(initial)).toContainEqual(move);
  });
});
