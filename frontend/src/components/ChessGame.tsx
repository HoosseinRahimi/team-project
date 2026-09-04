import { useEffect, useMemo, useState } from "react";

import {
  applyMove,
  chooseComputerMove,
  createInitialState,
  getStatus,
  legalMoves,
  moveToSan,
  squareName,
  type ChessState,
  type Color,
  type Move,
  type PieceType,
} from "../games/chess/engine";

const GLYPHS: Record<PieceType, string> = {
  king: "\u265A",
  queen: "\u265B",
  rook: "\u265C",
  bishop: "\u265D",
  knight: "\u265E",
  pawn: "\u265F",
};

const PROMOTION_CHOICES: PieceType[] = ["queen", "rook", "bishop", "knight"];

interface HistoryEntry {
  state: ChessState;
  mover: Color;
  move: Move | null;
  san: string | null;
}

type Mode = "computer" | "two-players";

function makeEntry(
  state: ChessState,
  mover: Color,
  move: Move | null,
  san: string | null,
): HistoryEntry {
  return { state, mover, move, san };
}

/** Pieces each side has captured (so `captured.white` holds black pieces). */
function capturedPieces(history: HistoryEntry[]): Record<Color, PieceType[]> {
  const captured: Record<Color, PieceType[]> = { white: [], black: [] };
  for (const { mover, move } of history.slice(1)) {
    if (move?.captured) captured[mover].push(move.captured);
  }
  return captured;
}

export default function ChessGame() {
  const [history, setHistory] = useState<HistoryEntry[]>([
    makeEntry(createInitialState(), "white", null, null),
  ]);
  const [selected, setSelected] = useState<number | null>(null);
  const [mode, setMode] = useState<Mode>("computer");
  const [thinking, setThinking] = useState(false);
  const [pendingPromotion, setPendingPromotion] = useState<Move[] | null>(null);

  const current = history[history.length - 1];
  const state = current.state;
  const status = useMemo(() => getStatus(state), [state]);
  const moves = useMemo(() => legalMoves(state), [state]);
  const over = status.result !== "in-progress";
  const blockedByMode = mode === "computer" && state.turn === "black";
  const interactive = !over && !thinking && !blockedByMode && !pendingPromotion;

  function commitMove(move: Move) {
    const san = moveToSan(state, move);
    const next = applyMove(state, move);
    setHistory((entries) => [...entries, makeEntry(next, state.turn, move, san)]);
  }

  function handleSquareClick(index: number) {
    if (!interactive) return;

    if (selected !== null) {
      const candidates = moves.filter((move) => move.from === selected && move.to === index);
      if (candidates.length > 1 && candidates.every((move) => move.promotion)) {
        setPendingPromotion(candidates);
        return;
      }
      if (candidates.length === 1) {
        commitMove(candidates[0]);
        setSelected(null);
        return;
      }
    }

    const piece = state.board[index];
    if (piece && piece.color === state.turn) {
      setSelected((previous) => (previous === index ? null : index));
    } else {
      setSelected(null);
    }
  }

  // Let the computer answer (as black) after a short pause.
  useEffect(() => {
    if (
      mode !== "computer" ||
      state.turn !== "black" ||
      getStatus(state).result !== "in-progress"
    ) {
      return;
    }
    setThinking(true);
    const timer = window.setTimeout(() => {
      const move = chooseComputerMove(state, 3);
      if (move) {
        const san = moveToSan(state, move);
        setHistory((entries) => [
          ...entries,
          makeEntry(applyMove(state, move), state.turn, move, san),
        ]);
      }
      setThinking(false);
    }, 250);
    return () => {
      window.clearTimeout(timer);
      setThinking(false);
    };
  }, [mode, state]);

  function undo() {
    setHistory((entries) => {
      if (entries.length <= 1) return entries;
      let next = entries.slice(0, -1);
      if (mode === "computer") {
        // Step back over the computer's reply so it is the player's turn again.
        while (next.length > 1 && next[next.length - 1].state.turn === "black") {
          next = next.slice(0, -1);
        }
      }
      return next;
    });
    setSelected(null);
    setPendingPromotion(null);
  }

  function reset() {
    setHistory([makeEntry(createInitialState(), "white", null, null)]);
    setSelected(null);
    setPendingPromotion(null);
  }

  const targets =
    selected === null
      ? new Set<number>()
      : new Set(moves.filter((move) => move.from === selected).map((move) => move.to));
  const captureTargets = new Set(
    selected === null
      ? []
      : moves.filter((move) => move.from === selected && move.captured).map((move) => move.to),
  );
  const last = current.move;
  const captured = capturedPieces(history);
  const checkSquare =
    status.inCheck && status.result === "in-progress"
      ? state.board.findIndex(
          (piece) => piece && piece.type === "king" && piece.color === state.turn,
        )
      : -1;

  const statusLabel = over
    ? status.result === "checkmate"
      ? `Checkmate — ${status.winner === "white" ? "White" : "Black"} wins`
      : "Stalemate — it is a draw"
    : thinking
      ? "Computer is thinking…"
      : `${state.turn === "white" ? "White" : "Black"} to move${status.inCheck ? " — check!" : ""}`;

  const sans = history.slice(1).map((entry) => entry.san ?? "");
  const moveRows: string[] = [];
  for (let index = 0; index < sans.length; index += 2) {
    moveRows.push(
      `${index / 2 + 1}. ${sans[index]}${sans[index + 1] ? `  ${sans[index + 1]}` : ""}`,
    );
  }

  return (
    <div className="chess-game">
      <div className="chess-board-frame">
        <div className="chess-board">
          {state.board.map((piece, index) => {
            const classes = [
              "chess-square",
              (Math.floor(index / 8) + (index % 8)) % 2 === 0 ? "light" : "dark",
            ];
            if (selected === index) classes.push("selected");
            if (last && (last.from === index || last.to === index)) classes.push("last-move");
            if (index === checkSquare) classes.push("in-check");
            if (targets.has(index))
              classes.push(captureTargets.has(index) ? "capture-target" : "move-target");
            return (
              <button
                type="button"
                key={index}
                className={classes.join(" ")}
                aria-label={`${squareName(index)}, ${piece ? `${piece.color} ${piece.type}` : "empty"}`}
                onClick={() => handleSquareClick(index)}
                disabled={!interactive && !targets.has(index)}
              >
                {piece ? (
                  <span className={`chess-piece ${piece.color}`} aria-hidden="true">
                    {GLYPHS[piece.type]}
                  </span>
                ) : null}
              </button>
            );
          })}
        </div>
        {pendingPromotion ? (
          <div className="chess-promotion" role="dialog" aria-label="Choose a promotion piece">
            <p>Promote to</p>
            <div>
              {PROMOTION_CHOICES.map((type) => (
                <button
                  type="button"
                  key={type}
                  className="chess-square light promotion-choice"
                  aria-label={`Promote to ${type}`}
                  onClick={() => {
                    const move = pendingPromotion.find((candidate) => candidate.promotion === type);
                    if (move) commitMove(move);
                    setPendingPromotion(null);
                    setSelected(null);
                  }}
                >
                  <span className={`chess-piece ${state.turn}`} aria-hidden="true">
                    {GLYPHS[type]}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <aside className="chess-panel">
        <p className={`chess-status${status.result === "checkmate" ? " decisive" : ""}`}>
          {statusLabel}
        </p>
        <div className="chess-captured">
          <p>
            <span>White took</span>
            <span className="chess-piece black" aria-hidden="true">
              {captured.white.map((type) => GLYPHS[type]).join("") || "—"}
            </span>
          </p>
          <p>
            <span>Black took</span>
            <span className="chess-piece white" aria-hidden="true">
              {captured.black.map((type) => GLYPHS[type]).join("") || "—"}
            </span>
          </p>
        </div>
        <ol className="chess-moves">
          {moveRows.map((row) => (
            <li key={row}>{row}</li>
          ))}
        </ol>
        <div className="chess-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={undo}
            disabled={history.length <= 1 || thinking}
          >
            Undo
          </button>
          <button type="button" className="secondary-button" onClick={reset}>
            New game
          </button>
          <button
            type="button"
            className="primary-button"
            onClick={() =>
              setMode((previous) => (previous === "computer" ? "two-players" : "computer"))
            }
          >
            {mode === "computer" ? "Two players" : "Play vs computer"}
          </button>
        </div>
      </aside>
    </div>
  );
}
