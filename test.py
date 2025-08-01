import sys
import os
import json
import time
import argparse
import asyncio
from datetime import datetime
import subprocess
from desktop_notifier import DesktopNotifier

# Configuration
ALARM_FILE = os.path.join(os.path.expanduser("~"), "alarms.json")
APP_NAME = "AlarmApp"
ICON_PATH = os.path.join(os.path.dirname(__file__), "alarm_icon.png")  # Optional icon

def save_alarm(alarm_time, message):
    """Save alarm to JSON file"""
    alarms = load_alarms()
    alarms.append({
        "time": alarm_time.strftime("%Y-%m-%d %H:%M"),
        "message": message
    })
    with open(ALARM_FILE, "w") as f:
        json.dump(alarms, f, indent=2)

def load_alarms():
    """Load existing alarms from JSON file"""
    try:
        with open(ALARM_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

async def show_notification(message):
    """Show desktop notification using desktop-notifier"""
    notifier = DesktopNotifier(app_name=APP_NAME)
    
    # Try to use icon if available
    icon = ICON_PATH if os.path.exists(ICON_PATH) else None
    
    await notifier.send(
        title="Alarm Triggered!",
        message=message,
        icon=icon,
        sound=True
    )

def check_alarms():
    """Check if any alarms should trigger"""
    alarms = load_alarms()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Find matching alarms
    triggered = [a for a in alarms if a["time"] == now]
    
    # Remove triggered alarms
    remaining = [a for a in alarms if a["time"] != now]
    
    with open(ALARM_FILE, "w") as f:
        json.dump(remaining, f, indent=2)
    
    # Show notifications
    for alarm in triggered:
        asyncio.run(show_notification(alarm["message"]))

def create_windows_task():
    """Create scheduled task to run every minute"""
    exe_path = os.path.abspath(sys.argv[0])
    task_name = "AlarmAppBackground"
    
    # Command to create scheduled task
    cmd = [
        'schtasks', '/Create', '/TN', task_name,
        '/TR', f'"{exe_path}" run',
        '/SC', 'MINUTE',
        '/F'  # Force create
    ]
    
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def list_alarms():
    """Show all scheduled alarms"""
    alarms = load_alarms()
    if not alarms:
        print("No alarms scheduled")
        return
    
    print("Scheduled Alarms:")
    for i, alarm in enumerate(alarms, 1):
        print(f"{i}. {alarm['time']} - {alarm['message']}")

def main():
    parser = argparse.ArgumentParser(
        description='Simple Alarm App',
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Set alarm command
    set_parser = subparsers.add_parser('set', help='Set a new alarm')
    set_parser.add_argument('time', help='Alarm time (YYYY-MM-DD HH:MM)')
    set_parser.add_argument('message', help='Message for the alarm')

    # Run background check
    subparsers.add_parser('run', help=argparse.SUPPRESS)  # Hidden command
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up background service')
    
    # List alarms command
    subparsers.add_parser('list', help='List all scheduled alarms')
    
    # Clear all alarms
    subparsers.add_parser('clear', help='Remove all scheduled alarms')

    args = parser.parse_args()

    if args.command == 'set':
        try:
            alarm_time = datetime.strptime(args.time, '%Y-%m-%d %H:%M')
            if alarm_time < datetime.now():
                print("Error: Can't set alarm in the past")
                return
            save_alarm(alarm_time, args.message)
            print(f"✅ Alarm set for {alarm_time.strftime('%Y-%m-%d %H:%M')}")
        except ValueError:
            print("❌ Invalid time format. Use: YYYY-MM-DD HH:MM")
    
    elif args.command == 'run':
        check_alarms()
    
    elif args.command == 'setup':
        create_windows_task()
        print("✅ Background service installed!\nAlarms will work even when app is closed.")
    
    elif args.command == 'list':
        list_alarms()
    
    elif args.command == 'clear':
        with open(ALARM_FILE, "w") as f:
            json.dump([], f)
        print("✅ All alarms cleared")

if __name__ == '__main__':
    # Create alarm file if not exists
    if not os.path.exists(ALARM_FILE):
        with open(ALARM_FILE, "w") as f:
            json.dump([], f)
    
    main()