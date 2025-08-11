# Quick Setup Guide

This guide will help you get ChessLM running quickly on your local machine.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- API keys for desired LLM providers (optional - you can start with Ollama for local models)

## Step-by-Step Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/davidzuma/chessLM.git
cd chessLM

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env
```

Add your API keys to the `.env` file:

```env
# Add only the providers you plan to use
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
MISTRAL_API_KEY=your_mistral_key_here
# Ollama doesn't need an API key (local models)
```

### 3. Run the Application

```bash
python app.py
```

The application will start and display a local URL (typically `http://127.0.0.1:7860`).

## Quick Start Options

### Option 1: Ollama (No API Key Required)
1. Install [Ollama](https://ollama.com/) locally
2. Pull a model: `ollama pull qwen3`
3. Set both players to "Ollama" with model "qwen3"
4. Start playing immediately!

### Option 2: Single Provider Setup
1. Get an API key from one provider (e.g., OpenAI)
2. Add it to your `.env` file or enter it in the UI
3. Set one player to "Human" and the other to your provider
4. Enter the model name (e.g., "gpt-4o" for OpenAI)

### Option 3: AI vs AI Battle
1. Configure two different providers with API keys
2. Set both White and Black to different AI providers
3. Watch them play automatically!

## Common Issues

### "Module not found" Error
```bash
# Make sure you're in the correct directory and dependencies are installed
pip install -r requirements.txt
```

### API Key Issues
- Double-check your API keys are correct
- Ensure the `.env` file is in the project root directory
- You can also enter API keys directly in the UI

### Model Name Issues
- Check the provider's documentation for correct model names
- Common examples:
  - OpenAI: `gpt-4o`, `gpt-4-turbo`
  - Anthropic: `claude-sonnet-4-20250514`
  - Gemini: `gemini-1.5-flash`
  - Mistral: `mistral-large-latest`
  - Ollama: `qwen3`, `llama3`

## Next Steps

Once you have the application running:

1. **Configure Players**: Choose Human or AI for White and Black
2. **Set Model Details**: Enter model names and API keys
3. **Start Playing**: Make moves on the board or chat with AI agents
4. **Experiment**: Try different AI providers and see how they play!

For more detailed information, see the main [README.md](README.md) file.
