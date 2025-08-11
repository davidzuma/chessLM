import chess
from langchain_core.tools import BaseTool, tool
from langchain_mcp_adapters.client import MultiServerMCPClient


def create_base_tools(board: chess.Board, allowed_side: str | None = None) -> list[BaseTool]:
    """Create tools for interacting with a chess board.

    Args:
        board (chess.Board): The chess board to interact with.
        allowed_side (str | None): If set to 'white' or 'black', only allow make_move
            when it's that side to move. Otherwise, allow any legal move.

    Returns:
        list[BaseTool]: A list of tools for interacting with the chess board.
    """

    @tool
    def get_fen() -> str:
        """Get the current FEN string of the chess board."""
        fen = board.fen()
        print(f"[tool:get_fen] {fen}")
        return fen

    @tool
    def set_fen(fen: str) -> str:
        """Set the chess board to a specific FEN string.
        Don't use when you are playing a game, use the `make_move` tool instead.

        Args:
            fen (str): The FEN string to set the board to.
        """
        print(f"[tool:set_fen] input={fen}")
        try:
            board.set_fen(fen)
            new_fen = board.fen()
            print(f"[tool:set_fen] new_fen={new_fen}")
            return new_fen
        except ValueError as e:
            print(f"[tool:set_fen][ERROR] {e}")
            return str(e)

    @tool
    def make_move(move: str) -> str:
        """Make a move on the chess board and return the new FEN string.

        Args:
            move (str): The move in UCI format (e.g., "e2e4", "g1f3", "e1g1" for castling).
                       UCI format is always: source_square + destination_square + promotion_piece (if any).
                       Examples: e2e4 (pawn), b1c3 (knight), f1c4 (bishop), e1g1 (kingside castle), 
                       e7e8q (pawn promotion to queen).
        """
        print(f"[tool:make_move] move={move}")
        try:
            # Enforce turn if restricted to a specific side
            if allowed_side is not None:
                current = "white" if board.turn == chess.WHITE else "black"
                if current != allowed_side:
                    msg = f"Not your turn: it's {current} to move. Wait for opponent."
                    print(f"[tool:make_move] {msg}")
                    return msg
            chess_move = chess.Move.from_uci(move)
            if chess_move in board.legal_moves:
                board.push(chess_move)
                new_fen = board.fen()
                status = "ongoing"
                if board.is_checkmate():
                    # After push, board.turn is the side with no legal moves; winner is the opposite
                    winner = "white" if board.turn == chess.BLACK else "black"
                    status = f"checkmate:{winner}"
                elif board.is_stalemate():
                    status = "stalemate"
                elif board.is_insufficient_material():
                    status = "draw:insufficient_material"
                elif board.can_claim_threefold_repetition():
                    status = "draw:threefold_repetition_claim_available"
                elif board.can_claim_fifty_moves():
                    status = "draw:fifty_move_rule_claim_available"
                print(f"[tool:make_move] ok new_fen={new_fen} status={status}")
                return f"{new_fen} | status={status}"
            else:
                print(f"[tool:make_move] illegal move={move}")
                legal_moves = [m.uci() for m in list(board.legal_moves)[:10]]
                return f"Illegal move '{move}'. Use UCI format like these legal moves: {', '.join(legal_moves)}"
        except Exception as e:
            print(f"[tool:make_move][ERROR] {e}")
            if "expected uci string" in str(e).lower() or "invalid uci" in str(e).lower():
                return f"Invalid UCI format '{move}'. Use convert_move_to_uci tool if you have algebraic notation, or get_legal_moves to see valid UCI moves."
            return str(e)

    @tool
    def get_legal_moves() -> str:
        """Get all legal moves in UCI format for the current position."""
        legal_moves = [move.uci() for move in board.legal_moves]
        legal_moves_str = ", ".join(legal_moves[:20])  # Limit to first 20 to avoid overwhelming output
        if len(list(board.legal_moves)) > 20:
            legal_moves_str += f", ... and {len(list(board.legal_moves)) - 20} more"
        print(f"[tool:get_legal_moves] {legal_moves_str}")
        return f"Legal moves (UCI format): {legal_moves_str}"

    @tool
    def convert_move_to_uci(algebraic_move: str) -> str:
        """Convert a move from algebraic notation to UCI format.
        
        Args:
            algebraic_move (str): Move in algebraic notation (e.g., "Nf3", "Bxe3", "O-O")
        """
        print(f"[tool:convert_move_to_uci] input={algebraic_move}")
        try:
            # Try to parse as algebraic notation
            move = board.parse_san(algebraic_move)
            uci_move = move.uci()
            print(f"[tool:convert_move_to_uci] {algebraic_move} -> {uci_move}")
            return f"UCI format: {uci_move}"
        except ValueError as e:
            print(f"[tool:convert_move_to_uci][ERROR] {e}")
            return f"Could not convert '{algebraic_move}' to UCI format. Error: {e}"

    @tool
    def get_status() -> str:
        """Return a summary of the current game status (turn, check, checkmate, stalemate, result)."""
        turn = "white" if board.turn == chess.WHITE else "black"
        status = [f"turn={turn}"]
        if board.is_checkmate():
            status.append("checkmate")
        if board.is_stalemate():
            status.append("stalemate")
        if board.is_check():
            status.append("check")
        status.append(f"result={board.result(claim_draw=True)}")
        summary = f"FEN={board.fen()} | " + ", ".join(status)
        print(f"[tool:get_status] {summary}")
        return summary

    return [
        get_fen,
        set_fen,
        make_move,
        get_legal_moves,
        convert_move_to_uci,
        get_status,
    ]


async def create_mcp_tools(
    url: str = "http://localhost:7860/gradio_api/mcp/sse", transport: str = "sse"
) -> list[BaseTool]:
    mcp_client = MultiServerMCPClient(
        {
            "chess": {
                "url": url,
                "transport": transport,
            }
        }
    )

    return await mcp_client.get_tools()
