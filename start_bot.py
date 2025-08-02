#!/usr/bin/env python3
"""
Enhanced startup script for the Azan Time Bot with better error handling
"""
import os
import sys
import time
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)

def check_environment():
    """Check if the environment is properly set up"""
    log.info("🔍 Checking environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        log.error("❌ .env file not found")
        log.error("Please create a .env file with your bot token:")
        log.error("BOT_TOKEN=your_bot_token_here")
        return False
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        log.info("✅ Virtual environment is active")
    else:
        log.warning("⚠️  Virtual environment not detected")
        log.warning("Consider activating your virtual environment first")
    
    # Check required files
    required_files = ['bot.py', 'config.py', 'handlers.py', 'utils.py', 'jobs.py', 'keyboards.py']
    for file in required_files:
        if not Path(file).exists():
            log.error(f"❌ Required file missing: {file}")
            return False
    
    log.info("✅ All required files found")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    log.info("📦 Checking dependencies...")
    
    required_packages = [
        'python-telegram-bot',
        'requests',
        'python-dotenv',
        'pytz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        log.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        log.error("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    log.info("✅ All dependencies are installed")
    return True

def run_bot_with_restart():
    """Run the bot with automatic restart on failure"""
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            log.info(f"🚀 Starting bot (attempt {restart_count + 1}/{max_restarts})...")
            
            # Run the bot
            result = subprocess.run([sys.executable, "bot.py"], 
                                  capture_output=False, 
                                  text=True)
            
            if result.returncode == 0:
                log.info("✅ Bot exited normally")
                break
            else:
                log.error(f"❌ Bot exited with code {result.returncode}")
                restart_count += 1
                
                if restart_count < max_restarts:
                    wait_time = min(30, 5 * restart_count)  # Progressive backoff
                    log.info(f"⏳ Waiting {wait_time} seconds before restart...")
                    time.sleep(wait_time)
                else:
                    log.error("❌ Maximum restart attempts reached")
                    break
                    
        except KeyboardInterrupt:
            log.info("🛑 Bot stopped by user")
            break
        except Exception as e:
            log.error(f"❌ Unexpected error: {e}")
            restart_count += 1
            
            if restart_count < max_restarts:
                wait_time = min(30, 5 * restart_count)
                log.info(f"⏳ Waiting {wait_time} seconds before restart...")
                time.sleep(wait_time)
            else:
                log.error("❌ Maximum restart attempts reached")
                break

def main():
    """Main function"""
    log.info("🤖 Azan Time Bot Startup Script")
    log.info("=" * 50)
    
    # Check environment
    if not check_environment():
        log.error("❌ Environment check failed")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        log.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Test bot token
    log.info("🔍 Testing bot token...")
    try:
        result = subprocess.run([sys.executable, "test_bot_token.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log.error("❌ Bot token test failed")
            log.error(result.stdout)
            log.error(result.stderr)
            sys.exit(1)
        else:
            log.info("✅ Bot token test passed")
    except subprocess.TimeoutExpired:
        log.error("❌ Bot token test timed out")
        sys.exit(1)
    except Exception as e:
        log.error(f"❌ Error testing bot token: {e}")
        sys.exit(1)
    
    log.info("=" * 50)
    log.info("🚀 All checks passed. Starting bot...")
    log.info("Press Ctrl+C to stop the bot")
    log.info("=" * 50)
    
    # Run bot with restart capability
    run_bot_with_restart()

if __name__ == "__main__":
    main()
