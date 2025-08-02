#!/usr/bin/env python3
"""
Bot management script for easy control of the Azan Time Bot
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def show_help():
    """Show help message"""
    print("🤖 Azan Time Bot Management Script")
    print("=" * 40)
    print("Usage: python3 manage_bot.py [command]")
    print()
    print("Commands:")
    print("  start     - Start the bot")
    print("  stop      - Stop the bot")
    print("  restart   - Restart the bot")
    print("  status    - Check bot status")
    print("  clear     - Clear webhook and prepare bot")
    print("  test      - Test bot token")
    print("  logs      - Show recent logs (if available)")
    print("  help      - Show this help message")
    print()

def get_bot_pid():
    """Get the PID of running bot process"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "python.*bot.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
        return None
    except:
        return None

def start_bot():
    """Start the bot"""
    print("🚀 Starting Azan Time Bot...")
    
    # Check if already running
    pid = get_bot_pid()
    if pid:
        print(f"⚠️  Bot is already running (PID: {pid})")
        return
    
    # Clear webhook first
    print("🧹 Clearing webhook...")
    subprocess.run([sys.executable, "clear_webhook.py"], check=False)
    
    # Start bot in background
    print("🤖 Starting bot...")
    subprocess.Popen([sys.executable, "bot.py"])
    
    # Wait a moment and check if it started
    time.sleep(2)
    pid = get_bot_pid()
    if pid:
        print(f"✅ Bot started successfully (PID: {pid})")
    else:
        print("❌ Failed to start bot")

def stop_bot():
    """Stop the bot"""
    print("🛑 Stopping Azan Time Bot...")
    
    pid = get_bot_pid()
    if not pid:
        print("ℹ️  Bot is not running")
        return
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        # Check if still running
        if get_bot_pid():
            print("⚠️  Bot didn't stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
        
        if not get_bot_pid():
            print("✅ Bot stopped successfully")
        else:
            print("❌ Failed to stop bot")
            
    except ProcessLookupError:
        print("✅ Bot was already stopped")
    except Exception as e:
        print(f"❌ Error stopping bot: {e}")

def restart_bot():
    """Restart the bot"""
    print("🔄 Restarting Azan Time Bot...")
    stop_bot()
    time.sleep(1)
    start_bot()

def check_status():
    """Check bot status"""
    print("📊 Checking bot status...")
    
    pid = get_bot_pid()
    if pid:
        print(f"✅ Bot is running (PID: {pid})")
        
        # Try to get more info about the process
        try:
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "pid,ppid,cmd,etime"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("Process info:")
                print(result.stdout)
        except:
            pass
    else:
        print("❌ Bot is not running")

def clear_webhook():
    """Clear webhook"""
    print("🧹 Clearing webhook...")
    result = subprocess.run([sys.executable, "clear_webhook.py"])
    if result.returncode == 0:
        print("✅ Webhook cleared")
    else:
        print("❌ Failed to clear webhook")

def test_token():
    """Test bot token"""
    print("🔍 Testing bot token...")
    result = subprocess.run([sys.executable, "test_bot_token.py"])
    if result.returncode == 0:
        print("✅ Token test completed")
    else:
        print("❌ Token test failed")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start_bot()
    elif command == "stop":
        stop_bot()
    elif command == "restart":
        restart_bot()
    elif command == "status":
        check_status()
    elif command == "clear":
        clear_webhook()
    elif command == "test":
        test_token()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
