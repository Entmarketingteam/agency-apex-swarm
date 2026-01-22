# Agency Apex Swarm (January 2026)

A cloud-native agent orchestration system for influencer lead generation, built with Claude Opus 4.5, GPT-5.2 Pro, and Gemini 3.0 Ultra.

## Architecture

This project uses **GitHub Codespaces** as the cloud environment, allowing you to work seamlessly across multiple computers (MacBook, Windows PC, Mac Mini) without losing state or configuration.

## Setup Instructions

> **Important**: This devcontainer is designed for **GitHub Codespaces** (cloud-based). You don't need Docker installed locally. If you see a Docker error, skip to Step 1 below.

### 1. Initial Setup (One-Time)

1. **Push this repo to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial setup: Apex environment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a Codespace** (No Docker needed!):
   - Go to your GitHub repo on github.com
   - Click the green **"Code"** button → **"Codespaces"** tab
   - Click **"..."** (three dots) → **"New with options"**
   - The devcontainer will be automatically detected
   - Click **"Create codespace"**
   - Wait 2-3 minutes for the environment to build

### 2. Connect Cursor to Codespace

1. **Install GitHub CLI** (if not installed):
   - Mac: `brew install gh`
   - Windows: `winget install GitHub.cli`

2. **Authenticate**:
   ```bash
   gh auth login
   ```

3. **Configure SSH**:
   ```bash
   gh codespace ssh --config >> ~/.ssh/config
   ```

4. **Connect in Cursor**:
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
   - Type "Remote-SSH: Connect to Host..."
   - Select your codespace from the list

### 3. Environment Variables

Add your API keys to Codespace Secrets:
- Go to your Codespace settings
- Add secrets for:
  - `ANTHROPIC_API_KEY` (for Claude Opus 4.5)
  - `OPENAI_API_KEY` (for GPT-5.2 Pro)
  - `GOOGLE_API_KEY` (for Gemini 3.0 Ultra)
  - `PERPLEXITY_API_KEY`
  - `FINDYMAIL_API_KEY`
  - `UNIPILE_API_KEY`
  - `SMARTLEAD_API_KEY`
  - `PINECONE_API_KEY`

Create a `.env` file in the root (this will be auto-populated from secrets):
```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
# ... etc
```

## Project Structure

```
agency-apex-swarm/
├── .devcontainer/          # Cloud environment config
│   └── devcontainer.json
├── .cursorrules            # Agent behavior rules
├── docs/                   # 📚 All documentation
│   ├── INDEX.md           # Start here - documentation index
│   ├── setup/             # Setup guides
│   ├── deployment/        # Deployment guides
│   ├── troubleshooting/   # Debug & fixes
│   └── reference/         # Playbook, schema, scenarios
├── main.py                 # Main orchestration script
├── run.py                  # Entry point (Railway/Production)
└── README.md              # This file
```

**📚 Documentation:** See [docs/INDEX.md](docs/INDEX.md) for complete documentation.

## Model Hierarchy (2026 Apex Stack)

- **The Architect**: Claude Opus 4.5 - Complex logic, planning, programmatic tool calling
- **The Strategist**: GPT-5.2 Pro - Financial modeling, high-stakes persuasion
- **The Scout**: Gemini 3.0 Ultra - Visual vibe checks, multimodal analysis
- **The Speedster**: Gemini 3 Flash - Daily terminal commands, quick edits
- **The Worker**: Claude Sonnet 4.5 - Code refactoring, routine tasks

## Workflow

1. **Plan**: Ask Opus 4.5 to review current workflow and optimize
2. **Execute**: Use programmatic tool calling to orchestrate multiple APIs
3. **Sync**: After successful changes, push to GitHub main

## Key Files

- `.cursorrules` - Tells the Agent how to behave and which models to use
- `docs/INDEX.md` - Complete documentation index
- `main.py` - Lead generation orchestrator
- `run.py` - Production entry point (Slack bot + Google Sheets scheduler)
- `.devcontainer/devcontainer.json` - Cloud environment configuration

## Documentation

**📚 All documentation is in `/docs/`:**

- **Getting Started:** [Quick Start](docs/setup/QUICKSTART.md)
- **Setup:** [Full Setup Guide](docs/setup/SETUP.md)
- **Slack Integration:** [Slack Bot Setup](docs/setup/SLACK.md)
- **Deployment:** [Railway Deployment](docs/deployment/RAILWAY.md)
- **Troubleshooting:** [Common Issues](docs/troubleshooting/COMMON_ISSUES.md)
- **Reference:** [System Playbook](docs/reference/PLAYBOOK.md)

## Troubleshooting

### Error: "Docker not found" or "spawn docker ENOENT"

**This is normal!** The devcontainer is for GitHub Codespaces, not local Docker.

**Solution**: 
- Ignore the local Docker error
- Push your code to GitHub first
- Create a Codespace (which has Docker built-in)
- Connect Cursor via SSH (see Step 2 above)

### I want to test locally first (Optional)

If you want to use the devcontainer locally before pushing to GitHub:

1. **Install Docker Desktop**:
   - Windows: Download from [docker.com](https://www.docker.com/products/docker-desktop)
   - Mac: `brew install --cask docker`

2. **Start Docker Desktop** (must be running)

3. **In Cursor**: Press `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

**Note**: For the multi-computer workflow, GitHub Codespaces is recommended over local Docker.

## Next Steps

1. Review `DOCS/CAPABILITIES.md` to understand tool selection
2. Create your main orchestration script using Opus 4.5
3. Test the workflow with a small batch of leads
4. Scale to 400 leads/day

