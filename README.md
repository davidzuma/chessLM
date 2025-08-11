---
tags: [agents, agent-demo-track, chess, chessboard, games]
title: Chess Agent
emoji: ♟️
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Play and chat chess against an LLM
---
# ChessLM ♟️🤖

**Interactive chess platform supporting Human vs AI, AI vs AI, or Human vs Human gameplay with multiple LLM providers.**

---

## What is ChessLM?

ChessLM is an advanced interactive chess platform that integrates multiple Large Language Model (LLM) capabilities. Unlike traditional chess interfaces, ChessLM allows you to:

* **Configure White and Black players independently** - choose Human or AI for each side
* **Support multiple AI providers** - Anthropic Claude, OpenAI GPT, Google Gemini, Mistral, and Ollama
* **Play moves** directly on an interactive chessboard with automatic AI turn execution
* **Chat with AI agents** via text messages, exploring their strategic reasoning in real-time
* **View transparent analysis** and tactical insights during gameplay

## Key Features 🚀

* **Dual Player Configuration:** Set White and Black players independently - Human, AI, or mixed combinations
* **Multiple AI Providers:**
  - **Anthropic** (Claude models)
  - **OpenAI** (GPT models)
  - **Google Gemini** (Gemini models)
  - **Mistral** (Mistral models)
  - **Ollama** (Local models)
* **Automatic AI Gameplay:** AI agents play moves automatically without manual intervention
* **Interactive Chessboard:** Make moves or set custom positions seamlessly
* **Real-time Chat Interface:** Communicate with AI agents during gameplay
* **Transparent Reasoning:** View step-by-step position analysis and internal AI reasoning
* **Environment Configuration:** Secure API key management via .env files

## How Does it Work? 🧠

ChessLM leverages advanced integrations and tools:

* [**Custom Gradio Component:**](https://huggingface.co/spaces/Agents-MCP-Hackathon/gradio_chessboard) Interactive chessboard interface implemented as a custom Gradio component for seamless board-LLM interaction
* **Multi-Provider Architecture:** Supports multiple LLM providers with automatic model routing and API key management
* **UCI Move Format:** Ensures consistent move notation across all AI providers for reliable gameplay
* **Automatic Turn Management:** AI vs AI games progress automatically with configurable move limits

These integrations compensate for LLMs' typical limitations in chess-playing ability, ensuring accurate and meaningful gameplay analysis.

## Use Cases

* **AI vs AI Analysis:** Watch different language models compete and analyze their strategic approaches
* **Educational Tool:** Learn chess strategies through transparent AI reasoning and position analysis
* **Mixed Play Modes:** Human vs AI with choice of opponent strength and model provider
* **Research Platform:** Compare chess-playing capabilities across different LLM providers
* **Interactive Chess Assistant:** Get real-time analysis and explanations during gameplay

## Getting Started 🚀

### Prerequisites

- Python 3.8 or higher
- API keys for desired LLM providers (optional for Ollama/local models)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/davidzuma/chessLM.git
   cd chessLM
   ```
2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API keys (optional):**
   Create a `.env` file in the project root:

   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   MISTRAL_API_KEY=your_mistral_key_here
   ```
4. **Run the application:**

   ```bash
   python app.py
   ```

### Usage

1. **Configure Players:** Select Human or AI provider for White and Black players
2. **Set Model Details:** Enter model names and API keys for AI players
3. **Start Playing:** Make moves on the board or chat with AI agents
4. **Watch AI vs AI:** Enable automatic gameplay between AI agents

## Supported Models

| Provider                | Example Models                                       | API Key Required |
| ----------------------- | ---------------------------------------------------- | ---------------- |
| **Anthropic**     | claude-sonnet-4-20250514, claude-3-5-sonnet-20241022 | Yes              |
| **OpenAI**        | gpt-4o, gpt-4-turbo, gpt-3.5-turbo                   | Yes              |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro                     | Yes              |
| **Mistral**       | mistral-large-latest, mistral-medium                 | Yes              |
| **Ollama**        | qwen3, llama3, codellama                             | No (local)       |
