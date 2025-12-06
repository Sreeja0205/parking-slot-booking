import os
import sys
import subprocess

print("🚀 Starting Parking Slot Booking deployment...")

# Step 1: Install Python dependencies
print("📦 Installing Python packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Step 2: Collect static files for production
print("🎨 Collecting static files...")
subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])

# Step 3: Apply database migrations
print("🗄️ Running database migrations...")
subprocess.check_call([sys.executable, "manage.py", "migrate"])

print("✅ Build completed successfully! Ready to deploy 🚗")
