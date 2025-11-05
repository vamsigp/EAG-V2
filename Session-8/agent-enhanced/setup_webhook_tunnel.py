"""
Helper script to set up a local webhook tunnel for Telegram bot.
Supports multiple tunneling services: ngrok, cloudflared (cloudflare tunnel).
"""

import os
import subprocess
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))


def check_command(command):
    """Check if a command is available in PATH."""
    try:
        subprocess.run([command, "--version"], 
                      capture_output=True, 
                      check=True,
                      timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def setup_ngrok():
    """Setup ngrok tunnel."""
    print("🌐 Setting up ngrok tunnel...")
    print("⚠️  Note: You need to install ngrok first: https://ngrok.com/download")
    print(f"📝 Once ngrok is running, it will expose port {WEBHOOK_PORT}")
    print(f"\n💡 To run ngrok manually:")
    print(f"   ngrok http {WEBHOOK_PORT}")
    print(f"\n📋 After starting ngrok:")
    print(f"   1. Copy the 'Forwarding' URL (e.g., https://xxxx.ngrok.io)")
    print(f"   2. Set it in your .env file as: TELEGRAM_WEBHOOK_URL=https://xxxx.ngrok.io")
    
    # Try to start ngrok automatically
    try:
        process = subprocess.Popen(
            ["ngrok", "http", str(WEBHOOK_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("\n✅ ngrok started! Check the terminal for the public URL.")
        print("   Press Ctrl+C to stop ngrok when done.")
        return process
    except FileNotFoundError:
        print("❌ ngrok not found. Please install it first.")
        return None


def setup_cloudflared():
    """Setup cloudflared tunnel (no signup required)."""
    print("🌐 Setting up cloudflared tunnel...")
    print("⚠️  Note: You need to install cloudflared first")
    print("   Windows: Download from https://github.com/cloudflare/cloudflared/releases")
    print("   Or use: winget install --id Cloudflare.cloudflared")
    
    if not check_command("cloudflared"):
        print("❌ cloudflared not found. Installing instructions:")
        print("   Windows: Download from https://github.com/cloudflare/cloudflared/releases")
        print("   Extract and add to PATH, or use: winget install --id Cloudflare.cloudflared")
        return None
    
    try:
        print(f"🚀 Starting cloudflared tunnel on port {WEBHOOK_PORT}...")
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{WEBHOOK_PORT}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait a moment for the URL to be generated
        time.sleep(3)
        
        # Try to extract URL from output (cloudflared prints it)
        print("\n⏳ Waiting for tunnel URL...")
        print("   Check the output above for a URL like: https://xxxx.trycloudflare.com")
        
        return process, None  # URL needs to be extracted manually
    except Exception as e:
        print(f"❌ Error starting cloudflared: {e}")
        return None, None


def configure_telegram_webhook(webhook_url):
    """Configure Telegram to send webhooks to the provided URL."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        return False
    
    webhook_endpoint = f"{webhook_url}/webhook"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
        response = requests.post(url, json={"url": webhook_endpoint}, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print(f"✅ Webhook configured successfully!")
            print(f"   URL: {webhook_endpoint}")
            return True
        else:
            print(f"❌ Failed to configure webhook: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error configuring webhook: {e}")
        return False


def main():
    """Main function to set up webhook tunnel."""
    print("=" * 60)
    print("🔧 Telegram Webhook Tunnel Setup")
    print("=" * 60)
    print()
    
    # Check if webhook server is running
    try:
        response = requests.get(f"http://localhost:{WEBHOOK_PORT}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ Webhook server is running on port {WEBHOOK_PORT}")
        else:
            print(f"⚠️  Webhook server might not be running on port {WEBHOOK_PORT}")
            print(f"   Start it first with: python webhook_server.py")
    except requests.exceptions.RequestException:
        print(f"⚠️  Webhook server is not running on port {WEBHOOK_PORT}")
        print(f"   Please start it first in another terminal:")
        print(f"   python webhook_server.py")
        return
    
    print("\nChoose a tunneling service:")
    print("1. ngrok (requires account, stable)")
    print("2. cloudflared (no account needed, Cloudflare)")
    print("3. Manual setup instructions")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        process = setup_ngrok()
        if process:
            print("\n📝 Once you have the ngrok URL:")
            print("   1. Copy it to your .env file as TELEGRAM_WEBHOOK_URL")
            print("   2. Restart webhook_server.py to auto-configure")
            print("\n   Or configure manually now:")
            url = input("   Enter the ngrok URL (e.g., https://xxxx.ngrok.io): ").strip()
            if url:
                configure_telegram_webhook(url)
    
    elif choice == "2":
        process, url = setup_cloudflared()
        if process:
            print("\n📝 Once you see the cloudflared URL:")
            print("   1. Copy it to your .env file as TELEGRAM_WEBHOOK_URL")
            print("   2. Restart webhook_server.py to auto-configure")
            print("\n   Or configure manually now:")
            url = input("   Enter the cloudflared URL: ").strip()
            if url:
                configure_telegram_webhook(url)
    
    elif choice == "3":
        print("\n📖 Manual Setup Instructions:")
        print("=" * 60)
        print("\nOption A: Using ngrok")
        print("  1. Install: https://ngrok.com/download")
        print(f"  2. Run: ngrok http {WEBHOOK_PORT}")
        print("  3. Copy the HTTPS URL (e.g., https://xxxx.ngrok.io)")
        print("  4. Set in .env: TELEGRAM_WEBHOOK_URL=https://xxxx.ngrok.io")
        print("\nOption B: Using cloudflared (no signup)")
        print("  1. Install: https://github.com/cloudflare/cloudflared/releases")
        print(f"  2. Run: cloudflared tunnel --url http://localhost:{WEBHOOK_PORT}")
        print("  3. Copy the HTTPS URL shown")
        print("  4. Set in .env: TELEGRAM_WEBHOOK_URL=<cloudflared-url>")
        print("\nOption C: Other services")
        print("  - localtunnel: npx localtunnel --port 8080")
        print("  - serveo: ssh -R 80:localhost:8080 serveo.net")
        print("\nAfter setting up:")
        print("  1. Make sure webhook_server.py is running")
        print("  2. Set TELEGRAM_WEBHOOK_URL in .env")
        print("  3. Restart webhook_server.py (it will auto-configure)")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted. Goodbye!")
        sys.exit(0)

