# Quick Setup Guide

## The Docker Error You're Seeing

**Don't worry!** The error about Docker not being found is expected. The `.devcontainer` folder is configured for **GitHub Codespaces** (cloud), not local Docker.

## Two Paths Forward

### ✅ Path 1: GitHub Codespaces (Recommended - No Docker Needed)

This is the path for working across multiple computers.

1. **Push to GitHub** (if you haven't already):
   ```bash
   git init
   git add .
   git commit -m "Initial Apex setup"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Codespace**:
   - Go to github.com → Your repo
   - Click green "Code" button → "Codespaces" tab
   - Click "..." → "New with options"
   - Click "Create codespace"
   - Wait 2-3 minutes

3. **Connect Cursor**:
   - Install GitHub CLI: `winget install GitHub.cli` (Windows) or `brew install gh` (Mac)
   - Run: `gh auth login`
   - Run: `gh codespace ssh --config >> ~/.ssh/config`
   - In Cursor: `Ctrl+Shift+P` → "Remote-SSH: Connect to Host..." → Select your codespace

**Done!** You're now working in the cloud. No Docker needed.

---

### 🔧 Path 2: Local Testing (Optional - Requires Docker)

Only do this if you want to test locally before pushing to GitHub.

1. **Install Docker Desktop**:
   - Download from [docker.com](https://www.docker.com/products/docker-desktop)
   - Start Docker Desktop (must be running)

2. **In Cursor**:
   - Press `Ctrl+Shift+P`
   - Type "Dev Containers: Reopen in Container"
   - Wait for container to build

**Note**: For your multi-computer workflow, Path 1 (Codespaces) is better.

---

## What Happens Next?

Once you're in the Codespace (or local container):

1. The environment auto-installs:
   - Python 3.11
   - Node.js
   - Anthropic SDK
   - Google Generative AI SDK
   - Pinecone client
   - Claude Code CLI

2. Add your API keys to Codespace Secrets (Settings → Secrets)

3. Start building! The Agent will read `.cursorrules` and `DOCS/CAPABILITIES.md` automatically.

---

## Still Stuck?

The Docker error is **not a problem** - it just means you're trying to use the devcontainer locally. Skip local Docker entirely and go straight to GitHub Codespaces (Path 1 above).

