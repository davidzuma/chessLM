from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Any

import gradio as gr
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
try:
    from langgraph.graph.graph import CompiledGraph  # type: ignore
except Exception:
    CompiledGraph = Any  # type: ignore

MESSAGE_TYPE = BaseMessage | gr.ChatMessage | dict[str, str]


def create_agent(
    model_name: str, provider: str, api_key: str, tools: list
):
    """Create a React agent with the specified model."""
    print(f"[create_agent] provider={provider} model={model_name} api_key_set={bool(api_key)}")
    model = _create_model(model_name, provider, api_key)
    # Ensure Ollama runs without reasoning/thinking for faster inference
    if provider == "Ollama":
        try:
            model = model.bind(think=False)
            print("[create_agent] Bound think=False for Ollama model")
        except Exception as _:
            # Binding is best-effort; model_kwargs in _create_model also sets think=False
            print("[create_agent] Warning: couldn't bind think=False; relying on model_kwargs")
    return create_react_agent(
        model,
        tools=tools,
    )


async def call_agent(
    agent, messages: list[MESSAGE_TYPE], prompt: HumanMessage
) -> AsyncIterator[list[MESSAGE_TYPE]]:
    print(f"[call_agent] prompt={prompt.content}")
    try:
        async for chunk in agent.astream(
            {
                "messages": [_convert_to_langchain_message(msg) for msg in messages[:-1]]
                + [prompt]
            }
        ):
            print(f"[call_agent] chunk keys={list(chunk.keys())}")
            if "tools" in chunk:
                for step in chunk["tools"]["messages"]:
                    print(f"[call_agent] tool step name={getattr(step,'name',None)} content={getattr(step,'content',None)}")
                    messages.append(
                        gr.ChatMessage(
                            role="assistant",
                            content=step.content,
                            metadata={"title": f"🛠️ Used tool {step.name}"},
                        )
                    )
                    yield messages
            if "agent" in chunk:
                content = _get_chunk_message_content(chunk)
                print(f"[call_agent] agent message={content}")
                messages.append(
                    gr.ChatMessage(
                        role="assistant",
                        content=content,
                    )
                )
                yield messages
    except Exception as e:
        print(f"[call_agent][ERROR] {e}")
        messages.append(gr.ChatMessage(role="assistant", content=f"Error: {e}"))
        yield messages


def _create_model(model_name: str, provider: str, api_key: str) -> BaseChatModel:
    """Get the chat model based on the provider and model name."""
    if provider == "Anthropic":
        return init_chat_model(
            "anthropic:" + model_name,
            anthropic_api_key=api_key,
        )
    elif provider == "Mistral":
        return init_chat_model(
            "mistralai:" + model_name,
            mistral_api_key=api_key,
        )
    elif provider == "OpenAI":
        return init_chat_model(
            "openai:" + model_name,
            openai_api_key=api_key,
        )
    elif provider == "Gemini":
        # Uses Google Generative AI via LangChain
        return init_chat_model(
            "google_genai:" + model_name,
            api_key=api_key,
        )
    elif provider == "Ollama":
        print(
            f"[_create_model] Using Ollama at http://localhost:11434 model={model_name} (think=False)"
        )
        # Pass think=False to disable reasoning traces for models that support it

        return init_chat_model(
            "ollama:" + model_name,
            base_url="http://localhost:11434",
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def _is_ai_message(message: MESSAGE_TYPE) -> bool:
    if isinstance(message, AIMessage):
        return True
    if isinstance(message, gr.ChatMessage):
        return message.role == "assistant"
    if isinstance(message, dict):
        return message.get("role") == "assistant"
    return False


def _convert_to_langchain_message(message: MESSAGE_TYPE) -> BaseMessage:
    if isinstance(message, BaseMessage):
        return message
    if isinstance(message, gr.ChatMessage):
        return (
            AIMessage(content=message.content)
            if _is_ai_message(message)
            else HumanMessage(content=message.content)
        )
    if isinstance(message, dict):
        return (
            AIMessage(content=message.get("content", ""))
            if _is_ai_message(message)
            else HumanMessage(content=message.get("content", ""))
        )
    raise ValueError(f"Unsupported message type: {type(message)}")


def _get_chunk_message_content(chunk: dict) -> str:
    msg_object = chunk["agent"]["messages"][0]
    message = msg_object.content
    if isinstance(message, list):
        message = message[0] if message else ""
    if isinstance(message, dict):
        message = message.get("text")
    return message or "Calling tool(s)"
