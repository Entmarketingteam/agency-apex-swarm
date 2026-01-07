#!/usr/bin/env python3
"""Automated Railway setup script."""

import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

RAILWAY_PROJECT_ID = "fdc4ef5d-702b-49e1-ab23-282b2fe90066"

# Environment variables to set
ENV_VARS = {
    "ANTHROPIC_API_KEY": config.ANTHROPIC_API_KEY,
    "OPENAI_API_KEY": config.OPENAI_API_KEY,
    "GOOGLE_API_KEY": config.GOOGLE_API_KEY,
    "PERPLEXITY_API_KEY": config.PERPLEXITY_API_KEY,
    "FINDYMAIL_API_KEY": config.FINDYMAIL_API_KEY,
    "UNIPILE_API_KEY": config.UNIPILE_API_KEY,
    "SMARTLEAD_API_KEY": config.SMARTLEAD_API_KEY,
    "PINECONE_API_KEY": config.PINECONE_API_KEY,
}


def run_command(cmd, check=True):
    """Run a shell command."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def check_railway_cli():
    """Check if Railway CLI is installed."""
    stdout, stderr, code = run_command("railway --version", check=False)
    if code == 0:
        logger.info(f"✅ Railway CLI found: {stdout}")
        return True
    else:
        logger.warning("⚠️ Railway CLI not found, attempting to install...")
        # Try to install
        install_cmd = "curl -fsSL https://railway.app/install.sh | sh"
        stdout, stderr, code = run_command(install_cmd, check=False)
        if code == 0:
            logger.info("✅ Railway CLI installed")
            # Update PATH
            railway_path = os.path.expanduser("~/.railway/bin")
            os.environ["PATH"] = f"{railway_path}:{os.environ.get('PATH', '')}"
            return True
        else:
            logger.error(f"❌ Failed to install Railway CLI: {stderr}")
            return False


def link_project():
    """Link to Railway project."""
    logger.info(f"🔗 Linking to Railway project: {RAILWAY_PROJECT_ID}")
    stdout, stderr, code = run_command(
        f"railway link {RAILWAY_PROJECT_ID}",
        check=False
    )
    if code == 0:
        logger.info("✅ Project linked successfully")
        return True
    else:
        logger.warning(f"⚠️ Link command output: {stdout} {stderr}")
        # May already be linked or need login
        return False


def set_environment_variables():
    """Set all environment variables in Railway."""
    logger.info("🔐 Setting environment variables...")
    
    success_count = 0
    for key, value in ENV_VARS.items():
        if not value:
            logger.warning(f"⚠️ Skipping {key} - no value in config")
            continue
        
        logger.info(f"Setting {key}...")
        # Escape the value for shell
        escaped_value = value.replace('"', '\\"').replace('$', '\\$')
        cmd = f'railway variables set {key}="{escaped_value}"'
        
        stdout, stderr, code = run_command(cmd, check=False)
        if code == 0:
            logger.info(f"✅ {key} set successfully")
            success_count += 1
        else:
            logger.error(f"❌ Failed to set {key}: {stderr}")
    
    logger.info(f"✅ Set {success_count}/{len(ENV_VARS)} environment variables")
    return success_count == len(ENV_VARS)


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("Railway Automated Setup")
    logger.info("=" * 60)
    
    # Check Railway CLI
    if not check_railway_cli():
        logger.error("❌ Railway CLI not available. Please install manually:")
        logger.error("   curl -fsSL https://railway.app/install.sh | sh")
        logger.error("\nThen run: railway login")
        return False
    
    # Check if logged in
    stdout, stderr, code = run_command("railway whoami", check=False)
    if code != 0:
        logger.warning("⚠️ Not logged in to Railway")
        logger.info("Please run: railway login")
        logger.info("This will open a browser for authentication")
        return False
    
    logger.info(f"✅ Logged in as: {stdout}")
    
    # Link project
    link_project()
    
    # Set environment variables
    if set_environment_variables():
        logger.info("\n" + "=" * 60)
        logger.info("✅ Setup complete!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Go to Railway dashboard to configure service")
        logger.info("2. Set Start Command: python scripts/scheduler.py")
        logger.info("3. Set Restart Policy: On Failure")
        logger.info("4. Deploy: railway up")
        return True
    else:
        logger.warning("\n⚠️ Some variables may not have been set")
        logger.info("Check Railway dashboard to verify")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

