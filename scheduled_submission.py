import schedule
import time
from datetime import datetime, timedelta
import subprocess
import sys
import os

def submit_job():
    print(f"\nSubmitting job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    script_path = os.path.join(os.path.dirname(__file__), 'pentagonal_resonance_circuit.py')
    result = subprocess.run([
        sys.executable,
        script_path,
        '--shots', '8192',
        '--submit'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

def main():
    # Schedule jobs from 22:00 to 23:15 every 5 minutes
    current_time = datetime.now()
    
    # Find today's or tomorrow's 22:00, whichever is next
    target_time = current_time.replace(hour=22, minute=0, second=0, microsecond=0)
    if current_time >= target_time:
        target_time += timedelta(days=1)
    
    # Calculate minutes until first run
    minutes_until_start = (target_time - current_time).total_seconds() / 60
    print(f"First job will run at {target_time.strftime('%Y-%m-%d %H:%M:%S')} "
          f"({minutes_until_start:.1f} minutes from now)")
    
    # Schedule the jobs
    schedule.every().day.at("22:00").do(submit_job)
    schedule.every().day.at("22:05").do(submit_job)
    schedule.every().day.at("22:10").do(submit_job)
    schedule.every().day.at("22:15").do(submit_job)
    schedule.every().day.at("22:20").do(submit_job)
    schedule.every().day.at("22:25").do(submit_job)
    schedule.every().day.at("22:30").do(submit_job)
    schedule.every().day.at("22:35").do(submit_job)
    schedule.every().day.at("22:40").do(submit_job)
    schedule.every().day.at("22:45").do(submit_job)
    schedule.every().day.at("22:50").do(submit_job)
    schedule.every().day.at("22:55").do(submit_job)
    schedule.every().day.at("23:00").do(submit_job)
    schedule.every().day.at("23:05").do(submit_job)
    schedule.every().day.at("23:10").do(submit_job)
    schedule.every().day.at("23:15").do(submit_job)
    
    print("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")

if __name__ == "__main__":
    main()
