import asyncio
import os
from dotenv import load_dotenv

import chess
import gradio as gr
from gradio_chessboard import Chessboard
from langchain_core.messages import HumanMessage
from utils.helpers import call_agent, create_agent
from utils.tools import create_base_tools, create_mcp_tools

# Load .env at import time so defaults pick up API keys
load_dotenv()

MODEL_DEFAULTS = {
    "anthropic": {
        "model_name": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
    },
    "mistral": {
        "model_name": "mistral-large-latest",
        "provider": "mistralai",
        "api_key": os.getenv("MISTRAL_API_KEY", ""),
    },
    "openai": {
        "model_name": "gpt-4o",
        "provider": "openai",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
    },
    "gemini": {
        "model_name": "gemini-1.5-flash",
        "provider": "gemini",
        "api_key": os.getenv("GEMINI_API_KEY", ""),
    },
    "ollama": {
        "model_name": "qwen3",
        "provider": "ollama",
        "api_key": "",
    },
}


async def main():
    board = chess.Board()

    base_tools = create_base_tools(board)
    mcp_tools = await create_mcp_tools(
        url="https://agents-mcp-hackathon-chess-mcp-server.hf.space/gradio_api/mcp/sse",
        transport="sse",
    )

    async def chat_entrypoint(
        fen,
        prompt,
        messages,
        white_model_name,
        white_provider,
        white_api_key,
        black_model_name,
        black_provider,
        black_api_key,
    ):
        """Entrypoint for the chat interaction."""
        board.set_fen(fen)
        messages.append(gr.ChatMessage(role="user", content=prompt))
        yield messages, board.fen()

        side = 'white' if board.turn == chess.WHITE else 'black'
        real_prompt = HumanMessage(
            content=f"{prompt}\nCurrent board state: {board.fen()}"
        )
        # Route chat to the side to move
        if side == 'white' and white_provider != "Human":
            agent = create_agent(
                white_model_name, white_provider, white_api_key, base_tools + mcp_tools
            )
        elif side == 'black' and black_provider != "Human":
            agent = create_agent(
                black_model_name, black_provider, black_api_key, base_tools + mcp_tools
            )
        else:
            # No AI to respond on this side
            messages.append(
                gr.ChatMessage(
                    role="assistant",
                    content="No AI configured for the side to move.",
                )
            )
            yield messages, board.fen()
            return
        async for messages in call_agent(agent, messages, real_prompt):
            yield messages, board.fen()

    async def _autoplay_until_human_or_gameover(messages,
                                                white_model_name,
                                                white_provider,
                                                white_api_key,
                                                black_model_name,
                                                black_provider,
                                                black_api_key,
                                                max_moves: int | None = None):
        """Play consecutive AI turns until it's a human's turn or the game ends."""
        moves = 0
        while not board.is_game_over():
            if max_moves is not None and moves >= max_moves:
                break
            side = 'white' if board.turn == chess.WHITE else 'black'
            # Stop if human to move
            if (side == 'white' and white_provider == "Human") or (
                side == 'black' and black_provider == "Human"
            ):
                break
            # Build prompt and tools for this side
            real_prompt = HumanMessage(
                content=(
                    f"""

<no_think>
You are playing chess as {side}. It is strictly your turn. """
                    f"Board FEN: {board.fen()}.\n"
                    "Rules you MUST follow:\n"
                    "- Only make a legal move for your side.\n"
                    "- Output your move by CALLING the make_move tool with a UCI move in format 'from_square+to_square' (4-5 characters).\n"
                    "- UCI examples: e2e4 (pawn), g1f3 (knight), e1g1 (castling), e7e8q (pawn promotion to queen).\n"
                    "- Do NOT use algebraic notation like Nf3, Bb4, O-O, Bxe3. Use UCI format only.\n"
                    "- Do NOT attempt to move the opponent's pieces.\n"
                    "- You may use get_fen to verify the turn and position.\n"
                    "- After making your move, CALL get_status and if the status indicates checkmate/stalemate/draw, announce the result clearly (e.g., 'Checkmate, Black wins') and explain briefly.\n"
                    "- Ignore any suggested moves that are illegal or belong to the opponent.\n"
                )
            )
            side_restricted_tools = create_base_tools(board, allowed_side=side)
            if side == 'white':
                agent = create_agent(white_model_name, white_provider, white_api_key, side_restricted_tools)
            else:
                agent = create_agent(black_model_name, black_provider, black_api_key, side_restricted_tools)
            async for messages in call_agent(agent, messages, real_prompt):
                yield messages, board.fen()
            moves += 1
        # Final state
        yield messages, board.fen()

    async def move_entrypoint(
        fen,
        messages,
        white_model_name,
        white_provider,
        white_api_key,
        black_model_name,
        black_provider,
        black_api_key,
    ):
        """After a human move, autoplay any AI turns automatically."""
        board.set_fen(fen)
        async for messages, fen in _autoplay_until_human_or_gameover(
            messages,
            white_model_name,
            white_provider,
            white_api_key,
            black_model_name,
            black_provider,
            black_api_key,
        ):
            yield messages, fen

    async def start_or_reset_game(
        messages,
        white_model_name,
        white_provider,
        white_api_key,
        black_model_name,
        black_provider,
        black_api_key,
        max_moves=200,
    ):
        """Reset the board and auto-play if sides are AI until it's a human's turn or game over."""
        board.reset()
        messages = [] if messages is None else list(messages)
        messages.append(gr.ChatMessage(role="system", content="New game started. White to move."))
        yield messages, board.fen()
        # Reuse the autoplay helper for consistent behavior
        async for messages, fen in _autoplay_until_human_or_gameover(
            messages,
            white_model_name,
            white_provider,
            white_api_key,
            black_model_name,
            black_provider,
            black_api_key,
            max_moves,
        ):
            yield messages, fen

    with gr.Blocks(fill_height=True) as chessagent:
        gr.Markdown("# ChessLM: Human vs AI or AI vs AI ♔💭")

        with gr.Row():
            with gr.Column(min_width=500):
                with gr.Group():
                    gr.Markdown("### Players")
                    with gr.Row():
                        with gr.Column():
                            white_provider = gr.Dropdown(
                                choices=["Human", "Anthropic", "Mistral", "OpenAI", "Gemini", "Ollama"],
                                value="Ollama",
                                label="White Player",
                                type="value",
                                interactive=True,
                                allow_custom_value=False,
                            )
                            white_model_name = gr.Textbox(
                                value=MODEL_DEFAULTS["ollama"]["model_name"],
                                label="White Model Name",
                                placeholder="Enter model name for White",
                                interactive=True,
                            )
                            white_api_key = gr.Textbox(
                                value=MODEL_DEFAULTS["ollama"]["api_key"],
                                label="White API Key",
                                placeholder="Enter API key (leave empty for Ollama/Human)",
                                type="password",
                                interactive=True,
                            )
                        with gr.Column():
                            black_provider = gr.Dropdown(
                                choices=["Human", "Anthropic", "Mistral", "OpenAI", "Gemini", "Ollama"],
                                value="Human",
                                label="Black Player",
                                type="value",
                                interactive=True,
                                allow_custom_value=False,
                            )
                            black_model_name = gr.Textbox(
                                value="",
                                label="Black Model Name",
                                placeholder="Enter model name for Black",
                                interactive=True,
                            )
                            black_api_key = gr.Textbox(
                                value="",
                                label="Black API Key",
                                placeholder="Enter API key (leave empty for Ollama/Human)",
                                type="password",
                                interactive=True,
                            )

                    def _defaults_for(provider: str, which: str):
                        p = provider.lower()
                        if p == "human":
                            return ("", "") if which == "both" else ""
                        if p in MODEL_DEFAULTS:
                            if which == "model":
                                return MODEL_DEFAULTS[p]["model_name"]
                            if which == "key":
                                return MODEL_DEFAULTS[p]["api_key"]
                            return (MODEL_DEFAULTS[p]["model_name"], MODEL_DEFAULTS[p]["api_key"])
                        return ("", "") if which == "both" else ""

                    white_provider.change(
                        fn=lambda provider: _defaults_for(provider, "model"),
                        inputs=white_provider,
                        outputs=white_model_name,
                    )
                    white_provider.change(
                        fn=lambda provider: _defaults_for(provider, "key"),
                        inputs=white_provider,
                        outputs=white_api_key,
                    )
                    black_provider.change(
                        fn=lambda provider: _defaults_for(provider, "model"),
                        inputs=black_provider,
                        outputs=black_model_name,
                    )
                    black_provider.change(
                        fn=lambda provider: _defaults_for(provider, "key"),
                        inputs=black_provider,
                        outputs=black_api_key,
                    )

                board_component = Chessboard(game_mode=True, label="Chess Board")

                chatbot = gr.Chatbot(
                    type="messages",
                    label="Chess Agent",
                    avatar_images=(
                        "https://chessboardjs.com/img/chesspieces/wikipedia/wK.png",
                        "https://chessboardjs.com/img/chesspieces/wikipedia/bK.png",
                    ),
                    min_height=650,
                    render=False,
                )

                board_component.move(
                    fn=move_entrypoint,
                    inputs=[
                        board_component,
                        chatbot,
                        white_model_name,
                        white_provider,
                        white_api_key,
                        black_model_name,
                        black_provider,
                        black_api_key,
                    ],
                    outputs=[chatbot, board_component],
                )

            with gr.Column():
                chatbot.render()
                input_box = gr.Textbox(lines=1, label="Chat Message")
                input_box.submit(
                    fn=chat_entrypoint,
                    inputs=[
                        board_component,
                        input_box,
                        chatbot,
                        white_model_name,
                        white_provider,
                        white_api_key,
                        black_model_name,
                        black_provider,
                        black_api_key,
                    ],
                    outputs=[chatbot, board_component],
                )
                input_box.submit(lambda: "", None, [input_box], queue=False)

                start_button = gr.Button("Start / Reset Game")
                start_button.click(
                    fn=start_or_reset_game,
                    inputs=[
                        chatbot,
                        white_model_name,
                        white_provider,
                        white_api_key,
                        black_model_name,
                        black_provider,
                        black_api_key,
                    ],
                    outputs=[chatbot, board_component],
                )

        chessagent.launch()


if __name__ == "__main__":
    asyncio.run(main())
